"""Saves on Postgres (interface.py). Every call that moves a game is one transaction holding the save's row
(SELECT ... FOR UPDATE), so two requests on one save run one after the other on any pod: read it (load.py), advance it
to the server's game time, apply the decision, write it (write.py). A decision whose `after` is not the save's count
is stale: the save is advanced and written as a plain advance instead, and Stale carries that. Game time is the wall
seconds since the save began, never before the time it was last written at (a pod's clock behind another's). Making,
deleting and restoring a save also hold the account (games.py).

A request advances under a time budget (BUDGET_S of wall time from when it began; stop_for makes each request's
stop), so a long absence is caught up in bounded slices, each written and committed, the page asking again until one
reaches now (Played.catching_up_to). A decision whose advance stops short is written as that slice and refused
(Behind)."""

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Connection, Engine

from .. import engine as e
from .. import logs
from ..accounts import limits
from ..clock import Clock
from ..db import reminders as reminder_rows
from ..db import saves as rows
from ..db import unit
from . import games as held
from . import write
from .games import info
from .interface import (
    MAX_SAVES, Behind, DecisionsLimited, Games, Info, Invalid, LastSave, NotFound, Opened, PastLine, Played, Ruleset,
    Stale,
    TooManySaves,
)
from .load import Loaded, load

HISTORY = 200
BUDGET_S = 3.0
"""Wall seconds one request may spend advancing: well under the gateway's 30 s, and short enough not to hold other
requests behind it in the pod's one process for long."""
_log = logging.getLogger("ashfall.saves")


def game_now(started_at: datetime, now: datetime, floor: int) -> int:
    return max(floor, int((now - started_at).total_seconds()))


def wall_budget() -> Callable[[], bool]:
    """A stop that says True once BUDGET_S of wall time has passed since it was made."""
    end = time.perf_counter() + BUDGET_S
    return lambda: time.perf_counter() >= end


class PgSaves:
    def __init__(self, engine: Engine, rs: Ruleset, clock: Clock,
                 stop_for: Callable[[], Callable[[], bool]] = wall_budget) -> None:
        """`stop_for` is called once per request, as it begins, for the stop its advance asks after each instant."""
        self._engine, self._rs, self._clock, self._stop_for = engine, rs, clock, stop_for

    def create(self, account_id: int) -> tuple[Info, Played]:
        rs, now = self._rs, self._clock()
        save = e.new_save(rs.rules)
        lines = tuple(e.Line(0, i, k) for i, k in enumerate(rs.start_lines))
        with unit.begin(self._engine) as conn:
            held.room(conn, account_id, held.hold(conn, account_id), now)
            purged = held.purge(conn, now)
            save_id = rows.insert_save(conn, account_id, now, write.written(save, 0, rs))
            rows.append_lines(conn, save_id, [(ln.time, str(ln.key)) for ln in lines])
            row = rows.save(conn, save_id, account_id)
        assert row is not None
        logs.info(_log, "save.created", account=account_id, save=save_id, number=row.number, lines=len(lines),
                  purged=purged)
        return info(row), Played(save_id=save_id, decisions=0, save=save, lines=lines)

    def list(self, account_id: int) -> list[Info]:
        with unit.read(self._engine) as conn:
            return [info(r) for r in rows.saves_of(conn, account_id)]

    def games(self, account_id: int) -> Games:
        with unit.read(self._engine) as conn:
            return held.listed(conn, account_id, self._clock())

    def delete(self, account_id: int, save_id: int) -> Games:
        now = self._clock()
        with unit.begin(self._engine) as conn:
            live = held.hold(conn, account_id)
            if rows.save(conn, save_id, account_id, lock=True) is None:
                raise NotFound(f"save {save_id}")
            if live <= 1:
                logs.info(_log, "save.delete_refused", account=account_id, save=save_id, reason="last_save")
                raise LastSave(f"save {save_id} is the account's only live save")
            rows.set_deleted(conn, save_id, now)
            purged = held.purge(conn, now)
            games = held.listed(conn, account_id, now)
        logs.info(_log, "save.deleted", account=account_id, save=save_id, live=live - 1, purged=purged)
        return games

    def restore(self, account_id: int, save_id: int) -> Games:
        now = self._clock()
        with unit.begin(self._engine) as conn:
            live = held.hold(conn, account_id)
            if rows.deleted_save(conn, save_id, account_id, now - held.KEPT) is None:
                raise NotFound(f"no held deleted save {save_id}")
            if live >= MAX_SAVES:
                logs.info(_log, "save.full", account=account_id, live=live)
                raise TooManySaves(f"account {account_id} holds {live}")
            rows.set_deleted(conn, save_id, None)
            games = held.listed(conn, account_id, now)
        logs.info(_log, "save.restored", account=account_id, save=save_id, live=live + 1)
        return games

    def open(self, account_id: int, save_id: int) -> Opened:
        t0, now, stop = time.perf_counter(), self._clock(), self._stop_for()
        with self._locked(account_id, save_id, visited=now) as (conn, row):
            loaded = load(row, self._rs)
            renamed, retired = self._rs.line_renames, self._rs.retired_lines
            history = tuple(PastLine(n=ln.n, at=ln.at, key=key)
                            for ln in rows.last_lines(conn, save_id, HISTORY)
                            if (key := renamed.get(ln.key, ln.key)) not in retired)
            played, now_row = self._write(conn, row, self._advanced(row, loaded, now, stop), now)
        logs.info(_log, "save.opened", account=account_id, save=save_id, game_at=played.save.time,
                  away_s=int((now - row.updated_at).total_seconds()), lines=len(played.lines),
                  rebased=loaded.rebased, behind_s=_behind_s(played), ms=_ms(t0))
        return Opened(info=info(now_row), was=loaded.save, history=history, presentation=dict(row.presentation or {}),
                      played=played)

    def advance(self, account_id: int, save_id: int) -> Played:
        t0, now, stop = time.perf_counter(), self._clock(), self._stop_for()
        with self._locked(account_id, save_id, visited=now) as (conn, row):
            loaded = load(row, self._rs)
            played = self._write(conn, row, self._advanced(row, loaded, now, stop), now).played
        behind = _behind_s(played)
        logs.emit(_log, logging.INFO if played.lines or behind is not None else logging.DEBUG, "save.advanced",
                  account=account_id, save=save_id, game_at=played.save.time, lines=len(played.lines),
                  rebased=loaded.rebased, behind_s=behind, ms=_ms(t0))
        return played

    def decide(self, account_id: int, save_id: int, verb: e.Verb, after: int) -> Played:
        t0, now, stop = time.perf_counter(), self._clock(), self._stop_for()
        fields: dict[str, object] = {"account": account_id, "save": save_id, "kind": write.KINDS[type(verb)],
                                     "target": _target(verb)}
        with self._locked(account_id, save_id) as (conn, row):
            loaded = load(row, self._rs)
            step = self._advanced(row, loaded, now, stop)
            stale, behind = after != row.decisions, step.catching_up_to is not None
            if not stale and not behind:
                self._counted(conn, save_id, now)
                try:
                    done = e.decide_logged(step.save, self._rs.rules, step.save.time, verb)
                except e.InvalidVerbError as ex:
                    logs.info(_log, "save.decision", **fields, n=row.decisions, game_at=step.save.time,
                              result="invalid", lines=0, rebased=loaded.rebased, ms=_ms(t0))
                    raise Invalid(str(ex)) from ex
                step = write.Step(done.save, write.numbered(step.lines, done.lines), verb, done.failed, done.context,
                                  step.rule_changes + done.rule_changes)
            played = self._write(conn, row, step, now).played
        logs.info(_log, "save.decision", **fields, n=played.decisions, game_at=played.save.time,
                  result="stale" if stale else "behind" if behind else "ok", lines=len(played.lines),
                  rebased=loaded.rebased, behind_s=_behind_s(played), ms=_ms(t0))
        if stale:
            raise Stale(played)
        if behind:
            raise Behind(played)
        return played

    def _counted(self, conn: Connection, save_id: int, now: datetime) -> None:
        refusal = limits.decided_in(conn, save_id, now)
        if refusal is not None:
            logs.warning(_log, "save.limited", save=save_id, scope=refusal.scope)
            raise DecisionsLimited(refusal.scope, refusal.retry_after_s)

    def current(self, account_id: int, save_id: int, stop: Callable[[], bool]) -> Played:
        row, done = self._read_now(account_id, save_id, stop)
        return Played(save_id=save_id, decisions=row.decisions, save=done.save, lines=())

    def forecast_stop(self) -> Callable[[], bool]:
        return self._stop_for()

    def dry_run(self, account_id: int, save_id: int, verbs: tuple[e.Verb, ...]) -> e.Save:
        _, done = self._read_now(account_id, save_id, self._stop_for())
        save = done.save
        at = save.time
        try:
            for verb in verbs:
                save = e.decide(save, self._rs.rules, at, verb)
        except e.InvalidVerbError as ex:
            raise Invalid(str(ex)) from ex
        return save

    def stored(self, account_id: int, save_id: int) -> e.Save:
        with unit.read(self._engine) as conn:
            row = rows.save(conn, save_id, account_id)
        if row is None:
            raise NotFound(f"save {save_id}")
        return load(row, self._rs).save

    def _read_now(self, account_id: int, save_id: int, stop: Callable[[], bool]) -> tuple[rows.SaveRecord, e.Step]:
        """The save as stored and advanced to now in memory, nothing written; Behind (the save as written) when that
        stops short. The replay holds no connection: the row is read and released first, and a refusal reads the
        save's repeats in a second short transaction."""
        now = self._clock()
        with unit.read(self._engine) as conn:
            row = rows.save(conn, save_id, account_id)
        unit.release()
        if row is None:
            raise NotFound(f"save {save_id}")
        loaded = load(row, self._rs)
        to = game_now(row.started_at, now, loaded.save.time)
        done = e.advance_logged(loaded.save, self._rs.rules, to, stop)
        if done.stopped_short:
            with unit.begin(self._engine) as conn:
                raise Behind(write.as_written(conn, row, loaded.save, self._rs, to))
        return row, done

    @contextmanager
    def _locked(self, account_id: int, save_id: int,
                visited: datetime | None = None) -> Generator[tuple[Connection, rows.SaveRecord]]:
        """`visited`: the player is here at that time, stamped for reminders in the lock's own statement."""
        visit = None if visited is None else reminder_rows.visit(account_id, visited)
        with unit.begin(self._engine) as conn:
            row = rows.save(conn, save_id, account_id, lock=True, visit=visit)
            if row is None:
                raise NotFound(f"save {save_id}")
            yield conn, row

    def _advanced(self, row: rows.SaveRecord, loaded: Loaded, now: datetime, stop: Callable[[], bool]) -> write.Step:
        to = game_now(row.started_at, now, loaded.save.time)
        done = e.advance_logged(loaded.save, self._rs.rules, to, stop)
        return write.Step(done.save, write.numbered(loaded.lines, done.lines), None,
                          rule_changes=loaded.rule_changes + done.rule_changes,
                          catching_up_to=to if done.stopped_short else None)

    def _write(self, conn: Connection, row: rows.SaveRecord, step: write.Step, now: datetime) -> write.Persisted:
        return write.persist(conn, row, step, self._rs, now)


def _target(verb: e.Verb) -> str | None:
    match verb:
        case e.TapCard(card=card):
            return str(card)
        case e.SwitchMix(mix=mix) | e.DeleteMix(mix=mix):
            return logs.tag(mix)   # a mix id is the player's own text
        case e.SaveMix(mix=mix):
            return logs.tag(mix.id)
        case e.AnswerOffer(offer=offer):
            return str(offer)
        case _:
            return None


def _behind_s(played: Played) -> int | None:
    """Game seconds the slice stopped short of its target; None when it reached it."""
    return None if played.catching_up_to is None else played.catching_up_to - played.save.time


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)
