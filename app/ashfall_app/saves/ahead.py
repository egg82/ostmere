"""A save's catch-up computed ahead while its player is away, so a return after a night opens caught up.

A busy save can cost minutes of engine time per night (a rule flipping every few game seconds is an instant each), far
more than a request's budget. So the job (`keep`, run each minute) advances each recently played save that has fallen
behind its clock, from its row as stored, loaded exactly as a step loads it (load.py, a rebase included), and keeps the
save it reached with that advance's lines and the rule runs it leaves (db/stored/ahead.py). A step that loads the very same
row under the same rules continues from there (`continuing`, `step`). An advance split at any instant is the advance
whole (engine `advance_logged`), and merged(gathered(r, c1), c2) == merged(r, c1 + c2) (ruleruns.py), so the step
writes what one advance from the row would have. Nothing is written to the save ahead of a step: its row, lines and
journal are the step's, as always, and any other row (a decision, a slice written) makes what is kept stale."""

import hashlib
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import Connection, Engine

from .. import engine as e
from .. import logs
from ..clock import Clock
from ..db.stored import ahead as kept_rows
from ..db import saves as rows
from ..db import unit
from ..engine.codec import Json
from .interface import Ruleset, Unavailable
from .builds.load import Loaded, load, newer
from .ruleruns import RuleRun, gathered, runs_from_json, runs_to_json
from .write import Step, numbered

VISITED_DAYS = 7
"""Saves written within this many days are kept ahead; a longer absence catches up on its return, in slices."""
MIN_BEHIND_S = 60
"""Game seconds a save may fall behind before the job advances it: a step covers that in well under a second."""
CHUNK_S = 10.0
"""Wall seconds of advancing between writes of what is kept, so a return mid-way finds the progress so far."""
_log = logging.getLogger("ashfall.saves")


@dataclass(frozen=True)
class Kept:
    """The save advanced from the row, that advance's lines (a rebase's are the step's own), and the rule runs it
    leaves, gathered from the row's."""

    save: e.Save
    lines: tuple[e.Line, ...]
    runs: tuple[RuleRun, ...]


def base_of(row: rows.SaveRecord) -> str:
    """What a step loads from the row, as one digest: a kept advance fits only the row it began from."""
    parts = (str(row.format), row.rules_digest, str(row.decisions), str(row.game_time), row.state,
             json.dumps(row.rule_runs, sort_keys=True))
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()


def continuing(conn: Connection, row: rows.SaveRecord, loaded: Loaded, rs: Ruleset) -> Kept | None:
    """What is kept ahead of `row` under `rs`, when it fits the row and reaches past it; else None. Read only when the
    row says something kept reaches past it, so a step at play's pace stays the round trips it was."""
    if row.ahead_at is None or row.ahead_at <= loaded.save.time:
        return None
    found = _fitting(kept_rows.kept(conn, row.id), row, loaded, rs)
    if found is not None:
        logs.info(_log, "save.ahead_used", save=row.id, ahead_s=found.save.time - loaded.save.time,
                  lines=len(found.lines))
    return found


def step(loaded: Loaded, kept: Kept | None, rules: e.Rules, to: int, stop: Callable[[], bool]) -> Step:
    """The step from the loaded row towards `to`, continuing what is kept when there is one."""
    if kept is None:
        start, lines, runs, changes = loaded.save, (), None, loaded.rule_changes
    else:
        start, lines, runs, changes = kept.save, kept.lines, kept.runs, ()
    to = max(to, start.time)   # kept by a job whose clock ran ahead of this pod's
    done = e.advance_logged(start, rules, to, stop)
    return Step(done.save, numbered(loaded.lines, lines + done.lines), None, loaded.save,
                rule_changes=changes + done.rule_changes, catching_up_to=to if done.stopped_short else None,
                runs_from=runs)


def keep(engine: Engine, rules_for: Callable[[], Ruleset], clock: Clock, run_s: float) -> int:
    """Advances every save that has fallen behind for at most `run_s` wall seconds in all; the game seconds kept."""
    t0, now = time.perf_counter(), clock()
    with unit.read(engine) as conn:
        ids = kept_rows.behind(conn, now, now - timedelta(days=VISITED_DAYS), MIN_BEHIND_S)
    gained = chunks = 0
    if ids:
        rs, run_end = rules_for(), t0 + run_s
        for save_id in ids:
            with kept_rows.claimed(engine, save_id) as mine:
                while mine and time.perf_counter() < run_end:
                    chunks += 1
                    got = _chunk(engine, rs, clock, save_id, min(run_end, time.perf_counter() + CHUNK_S))
                    gained += got or 0
                    if not got:
                        break
    logs.info(_log, "ahead.run", saves=len(ids), chunks=chunks, game_s=gained, ms=int((time.perf_counter() - t0) * 1000))
    return gained


def _chunk(engine: Engine, rs: Ruleset, clock: Clock, save_id: int, end: float) -> int | None:
    """One stretch of advancing the save, kept: the game seconds it gained; None when there is nothing to do (or the
    save is not this build's to read), 0 when what it reached was not kept (another job kept further)."""
    t0 = time.perf_counter()
    with unit.read(engine) as conn:
        row, rec = rows.save(conn, save_id, None), kept_rows.kept(conn, save_id)
    if row is None or newer(row, rs):
        return None
    try:
        loaded = load(row, rs)
    except Unavailable:
        return None
    start = _fitting(rec, row, loaded, rs) or Kept(loaded.save, (), gathered(runs_from_json(row.rule_runs),
                                                                              loaded.rule_changes))
    now = clock()
    to = int((now - row.started_at).total_seconds())
    if to - start.save.time <= MIN_BEHIND_S:
        return None
    done = e.advance_logged(start.save, rs.rules, to, lambda: time.perf_counter() >= end)
    reached = Kept(done.save, start.lines + done.lines, gathered(start.runs, done.rule_changes))
    record = kept_rows.AheadRecord(row.id, base_of(row), rs.digest, rs.release, done.save.time,
                                   e.encode(done.save, rs.rules), lines_to_json(reached.lines),
                                   runs_to_json(reached.runs))
    with unit.begin(engine) as conn:
        stored = kept_rows.keep(conn, record, now)
    gained = done.save.time - start.save.time
    logs.info(_log, "ahead.kept", save=row.id, game_at=done.save.time, gained_s=gained, behind_s=to - done.save.time,
              lines=len(reached.lines), rebased=loaded.rebased, stored=stored, ms=int((time.perf_counter() - t0) * 1000))
    return gained if stored else 0


def _fitting(rec: kept_rows.AheadRecord | None, row: rows.SaveRecord, loaded: Loaded, rs: Ruleset) -> Kept | None:
    if rec is None or rec.rules_digest != rs.digest or rec.game_time <= loaded.save.time or rec.base != base_of(row):
        return None
    try:
        return Kept(e.decode(rec.state, rs.rules), lines_from_json(rec.lines), runs_from_json(rec.rule_runs))
    except e.StateFormatError:
        logs.warning(_log, "save.ahead_unreadable", save=row.id)
        return None


def lines_to_json(lines: tuple[e.Line, ...]) -> Json:
    return [[ln.time, ln.seq, str(ln.key), None if ln.card is None else str(ln.card)] for ln in lines]


def lines_from_json(value: Json) -> tuple[e.Line, ...]:
    """What lines_to_json wrote; StateFormatError for anything else."""
    if not isinstance(value, list):
        raise e.StateFormatError("kept lines are not a list")
    return tuple(_line(item) for item in value)


def _line(item: Json) -> e.Line:
    if isinstance(item, list) and len(item) == 4:
        t, seq, key, card = item
        if isinstance(t, int) and isinstance(seq, int) and isinstance(key, str) and (card is None or isinstance(card, str)):
            return e.Line(t, seq, e.LineKey(key), None if card is None else e.CardId(card))
    raise e.StateFormatError("a kept line is not [time, seq, key, card]")
