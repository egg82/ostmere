"""The journal's composed days (tables.save_journal) and the lines they are composed from, read in the caller's
transaction. A step reads them in its save's locking statement (`locked`), so a decision that closes a day still holds
the row over the round trips db/test_decision_lock_span.py counts; its days are written by its one statement
(db/step.py). What is composed when is saves/ (journal_write.py); this module only reads."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, CTE, Connection, Label, Text, bindparam, case, func, literal_column, select
from sqlalchemy.dialects.postgresql import TIMESTAMP, aggregate_order_by

from .saves import SaveRecord, save_and
from .tables import save_journal, save_lines, saves

DAY_S = 86400


@dataclass(frozen=True)
class DayRecord:
    day: int
    notes: Any
    """The day's notes in page order, as JSON reads back: a list of {subject, slot, key}."""
    gap: str | None


@dataclass(frozen=True)
class Seen:
    """What a save's locking statement read of its journal."""

    next_day: int
    """The day after the newest stored, 0 for none."""
    fresh: bool
    """The statement's snapshot holds the save's row as locked. When the lock waited on another write to the save, the
    row is that write's but the snapshot is from before it, so the days and lines read here may lack what it stored."""
    days: list[DayRecord] | None
    """Every stored day, oldest first; None unless a day ends by the request's game time that none stored covers."""
    lines: list[tuple[int, str]] | None
    """The save's lines, (game second, key), carrying one of the keys asked, at a game time before the end of the last
    day ended by the request's game time; None when `days` is."""


def locked(conn: Connection, save_id: int, account_id: int, visit: CTE | None, keys: Sequence[str],
           now: datetime) -> tuple[SaveRecord, Seen] | None:
    """The save's row, locked (saves.save), and what its journal holds as of a request at wall time `now`."""
    found = save_and(conn, save_id, account_id, True, visit, _SEEN, {"j_now": now, "j_keys": list(keys)})
    if found is None:
        return None
    record, r = found
    return record, Seen(r.j_next, r.j_fresh, None if r.j_days is None else [DayRecord(*d) for d in r.j_days],
                        None if r.j_lines is None else [(at, key) for at, key in r.j_lines])


def _seen_columns() -> list[Label[Any]]:
    """`locked`'s columns, built once with bound parameters (`j_now`, `j_keys`) so a step does not rebuild them."""
    j, ln = save_journal.c, save_lines.c
    snap = saves.alias("snap")
    next_day = select(func.coalesce(func.max(j.day) + 1, 0)).where(j.save_id == saves.c.id).scalar_subquery()
    played = func.extract("epoch", bindparam("j_now", type_=TIMESTAMP(timezone=True)) - saves.c.started_at)
    ended = func.floor(func.greatest(saves.c.game_time, played) / DAY_S)
    due = next_day < ended
    days = select(func.coalesce(func.json_agg(aggregate_order_by(func.json_build_array(j.day, j.notes, j.gap), j.day)),
                                literal_column("'[]'::json"))).where(j.save_id == saves.c.id).scalar_subquery()
    lines = select(func.coalesce(func.json_agg(aggregate_order_by(func.json_build_array(ln.at, ln.key), ln.n)),
                                 literal_column("'[]'::json"))).where(
        ln.save_id == saves.c.id, ln.key == func.any(bindparam("j_keys", type_=ARRAY(Text))),
        ln.at < ended * DAY_S).scalar_subquery()
    fresh = literal_column("saves.xmin") == select(literal_column("snap.xmin", Text)).where(
        snap.c.id == saves.c.id).scalar_subquery()
    return [next_day.label("j_next"), fresh.label("j_fresh"), case((due, days)).label("j_days"),
            case((due, lines)).label("j_lines")]


_SEEN = _seen_columns()


def days(conn: Connection, save_id: int) -> list[DayRecord]:
    """Every stored day of the save, oldest first."""
    j = save_journal.c
    rows = conn.execute(select(j.day, j.notes, j.gap).where(j.save_id == save_id).order_by(j.day))
    return [DayRecord(day=r.day, notes=r.notes, gap=r.gap) for r in rows]


def lines_of(conn: Connection, save_id: int, keys: Sequence[str], before: int) -> list[tuple[int, str]]:
    """The save's lines, (game second, key), carrying one of `keys` at a game time before `before`, in order."""
    c = save_lines.c
    rows = conn.execute(select(c.at, c.key).where(c.save_id == save_id, c.key.in_(keys), c.at < before)
                        .order_by(c.n))
    return [(r.at, r.key) for r in rows]

