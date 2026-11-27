"""Writing a save after a step, in the step's transaction: the row (state, counters, which build wrote it), the lines
the step added, the journal days it wrote in (journal_write.py), and for a decision its log entry and, the first of a UTC
day, that day's snapshot. The writer keeps
its own retention: decisions past DECISIONS_KEPT and snapshots past SNAPSHOT_DAYS go as new ones come in. Lines are
earned history and never pruned."""

from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import NamedTuple

from sqlalchemy import Connection

from .. import engine as e
from ..db import saves as rows
from ..db.stored.journal import Seen
from ..db.stored.manifests import without
from ..db.stored.step import Log, write_step
from ..engine.codec import Json
from . import journal_write, mixbest
from .interface import Played, Ruleset
from .repeats import Logged, Repeats, count, hands_cards, since
from .ruleruns import RuleRun, gathered, merged, pruned, runs_from_json, runs_to_json, standing

DECISIONS_KEPT = timedelta(days=30)
SNAPSHOT_DAYS = 30
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)

KINDS: dict[type, str] = {e.TapCard: "tap_card", e.SwitchMix: "switch_mix", e.SaveMix: "save_mix",
                          e.DeleteMix: "delete_mix", e.SetOrders: "set_orders", e.SetQueue: "set_queue",
                          e.AnswerOffer: "answer_offer", e.AnswerKind: "answer_kind", e.Prestige: "prestige",
                          e.UndoPick: "undo_pick", e.MovePick: "move_pick"}
"""Each verb's kind, as the API names it (api/models.py Decision); prestige and undo_pick are not served yet."""


@dataclass(frozen=True)
class Step:
    """What a write records: the save after the step, its lines, and the verb decided, if any (and the card, if that
    verb was a failed tap)."""

    save: e.Save
    lines: tuple[e.Line, ...]
    verb: e.Verb | None
    began: e.Save
    """The save the step advanced from, as loaded (the journal reads the lost tallies between, journal_tallies.py)."""
    failed: e.CardId | None = None
    context: e.DecisionContext | None = None
    rule_changes: tuple[e.RuleChange, ...] = ()
    catching_up_to: int | None = None
    """The game time the step was advancing to, when it stopped short of it (Played.catching_up_to)."""
    runs_from: tuple[RuleRun, ...] | None = None
    """The rule runs `rule_changes` apply to when not the row's: those an advance kept ahead left (ahead.py)."""


class Persisted(NamedTuple):
    """A step written: what was played, and the save's row as written."""

    played: Played
    row: rows.Listed


def day_of(now: datetime) -> int:
    """The UTC day number (days since 1970-01-01)."""
    return (now - _EPOCH).days


def numbered(first: tuple[e.Line, ...], then: tuple[e.Line, ...]) -> tuple[e.Line, ...]:
    """`first` (a rebase's lines), then `then` with seq numbered on after first's lines at the same instant, so
    (time, seq) stays unique in one answer."""
    return first + tuple(replace(ln, seq=ln.seq + sum(1 for f in first if f.time == ln.time)) for ln in then)


def written(save: e.Save, decisions: int, rs: Ruleset, runs: tuple[RuleRun, ...] = (),
            best: Json = None) -> rows.Written:
    """The row of `save` under `rs`: its state without the manifest when `rs` holds it apart, whole otherwise."""
    state = e.encode(save, rs.rules)
    if rs.held_manifest is not None:
        state = without(state, rs.held_manifest)
    return rows.Written(state=state, format=e.FORMAT, rules_digest=rs.digest, decisions=decisions,
                        game_time=save.time, ended_at=save.ended_at, build=rs.build, release=rs.release,
                        camp_level=camp_level(save, rs), rule_runs=runs_to_json(runs), mix_best=best)


def _best(row: rows.SaveRecord, step: Step, rs: Ruleset) -> Json:
    """The save's kept best after a SaveMix step (mixbest.py), None (leave what is stored) for any other step."""
    verb = step.verb
    if rs.mix_marks is None or not isinstance(verb, e.SaveMix):
        return None
    mix = verb.mix.id
    return mixbest.to_json(mixbest.merged(mixbest.from_json(row.mix_best), mix, step.save.time,
                                          rs.mix_marks(step.save, mix)))


def camp_level(save: e.Save, rs: Ruleset) -> int:
    """How many Camp levels the save has landed: its camp triggers that fired."""
    return sum(1 for i in rs.camp_triggers if i < len(save.fired) and save.fired[i])


def persist(conn: Connection, row: rows.SaveRecord, seen: Seen | None, step: Step, rs: Ruleset,
            now: datetime) -> Persisted:
    """`seen`: what the save's locking statement read of its journal (db/journal.py `locked`), None for rules with
    none."""
    save_id, decisions = row.id, row.decisions + (step.verb is not None)
    before = runs_from_json(row.rule_runs) if step.runs_from is None else step.runs_from
    best = _best(row, step, rs)
    if step.catching_up_to is None:
        runs = merged(before, step.rule_changes, standing(step.save.orders, step.save.queue))
    else:
        runs = gathered(before, step.rule_changes)
    days, journaled = journal_write.composed(conn, row, seen, step.lines, step.began, step.save, rs)
    listed, recent = write_step(
        conn, save_id, now, written(step.save, decisions, rs, runs, best), [(ln.time, str(ln.key)) for ln in step.lines],
        None if step.verb is None else _log_of(decisions, step, rs, now),
        None if rs.repeats is None else since(rs.repeats, step.save.time), journaled)
    played = Played(save_id=save_id, decisions=decisions, save=step.save, lines=step.lines, failed=step.failed,
                    repeats=_counted(recent, step.save.time, rs), rule_runs=pruned(runs, step.save.orders),
                    catching_up_to=step.catching_up_to, days=days)
    return Persisted(played, listed)


def as_written(conn: Connection, row: rows.SaveRecord, save: e.Save, rs: Ruleset, catching_up_to: int) -> Played:
    """The save as its row holds it, nothing written: what a refusal that writes nothing (Behind on a dry run)
    carries."""
    return Played(save_id=row.id, decisions=row.decisions, save=save, lines=(),
                  repeats=repeated(conn, row.id, save.time, rs),
                  rule_runs=pruned(runs_from_json(row.rule_runs), save.orders), catching_up_to=catching_up_to)


def repeated(conn: Connection, save_id: int, now: int, rs: Ruleset) -> Repeats:
    """The save's repeats as of game time `now`, read off its logged decisions (repeats.py)."""
    if rs.repeats is None:
        return Repeats()
    return _counted(rows.recent_decisions(conn, save_id, since(rs.repeats, now)), now, rs)


def _counted(recent: list[rows.DecisionRecord], now: int, rs: Ruleset) -> Repeats:
    if rs.repeats is None:
        return Repeats()
    log = [Logged(d.at, e.verb_from_json(d.verb), e.context_from_json(d.context)) for d in recent]
    return count(log, now, hands_cards(rs.rules), rs.repeats)


def _log_of(n: int, step: Step, rs: Ruleset, now: datetime) -> Log:
    assert step.verb is not None
    entry = rows.DecisionRecord(n=n, at=step.save.time, kind=KINDS[type(step.verb)],
                                verb=e.verb_to_json(step.verb), rules_digest=rs.digest,
                                context=None if step.context is None else e.context_to_json(step.context))
    today = day_of(now)
    return Log(entry, now - DECISIONS_KEPT, today, today - SNAPSHOT_DAYS)
