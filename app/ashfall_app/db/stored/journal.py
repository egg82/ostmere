"""The journal's composed days (tables.save_journal) and the lines they are composed from, read in the caller's
transaction. A step reads them in its save's locking statement (`locked`), so a decision still holds the row over the
round trips tests/db/stored/test_decision_lock_span.py counts; its days are written by its one statement (db/stored/step.py). What is
composed when is saves/ (journal_write.py); this module only reads."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import ARRAY, CTE, Connection, Integer, Label, Text, bindparam, func, literal_column, select
from sqlalchemy.dialects.postgresql import aggregate_order_by

from ..saves import LineRecord, SaveRecord, save_and
from ..tables import save_journal, save_lines, saves

DAY_S = 86400


@dataclass(frozen=True)
class DayRecord:
    day: int
    notes: Any
    """The day's notes in page order, as JSON reads back: a list of {subject, slot, key}, a fold note with its count."""
    gap: str | None
    marks: Any
    """The kinds of mark its page carries, as JSON reads back: a list of strings."""
    through: int
    """The save time it was composed through; before the day's end while it is still being written."""


@dataclass(frozen=True)
class Seen:
    """What a save's locking statement read of its journal."""

    fresh: bool
    """The statement's snapshot holds the save's row as locked. When the lock waited on another write to the save, the
    row is that write's but the snapshot is from before it, so the days and lines read here may lack what it stored."""
    days: list[DayRecord]
    """Every stored day, oldest first."""
    lines: list[tuple[int, str]]
    """The save's lines, (game second, key), carrying one of the keys asked, in the order stored."""
    history: list[LineRecord] | None = None
    """The save's last lines, oldest first, when `locked` was asked for them; None when it was not."""


def locked(conn: Connection, save_id: int, account_id: int, visit: CTE | None, keys: Sequence[str],
           history: int | None = None) -> tuple[SaveRecord, Seen] | None:
    """The save's row, locked (saves.save), and what its journal holds; with `history`, its last that many lines too,
    read in the same statement (so, like the days, they may lack a write the lock waited on: check `fresh`)."""
    extra = _SEEN if history is None else [*_SEEN, _HISTORY]
    found = save_and(conn, save_id, account_id, True, visit, extra, {"j_keys": list(keys), "j_history": history})
    if found is None:
        return None
    record, r = found
    last = None if history is None else [LineRecord(*line) for line in reversed(r.j_history)]
    return record, Seen(r.j_fresh, [DayRecord(*d) for d in r.j_days], [(at, key) for at, key in r.j_lines], last)


def _seen_columns() -> list[Label[Any]]:
    """`locked`'s columns, built once with a bound parameter (`j_keys`) so a step does not rebuild them."""
    j, ln = save_journal.c, save_lines.c
    snap = saves.alias("snap")
    days = select(func.coalesce(func.json_agg(aggregate_order_by(
        func.json_build_array(j.day, j.notes, j.gap, j.marks, j.through), j.day)),
        literal_column("'[]'::json"))).where(j.save_id == saves.c.id).scalar_subquery()
    lines = select(func.coalesce(func.json_agg(aggregate_order_by(func.json_build_array(ln.at, ln.key), ln.n)),
                                 literal_column("'[]'::json"))).where(
        ln.save_id == saves.c.id, ln.key == func.any(bindparam("j_keys", type_=ARRAY(Text)))).scalar_subquery()
    fresh = literal_column("saves.xmin") == select(literal_column("snap.xmin", Text)).where(
        snap.c.id == saves.c.id).scalar_subquery()
    return [fresh.label("j_fresh"), days.label("j_days"), lines.label("j_lines")]


def _history_column() -> Label[Any]:
    """The save's last `j_history` lines as JSON, newest first, built once with a bound limit."""
    ln = save_lines.c
    last = select(ln.n, ln.at, ln.key).where(ln.save_id == saves.c.id).order_by(ln.n.desc()).limit(
        bindparam("j_history", type_=Integer)).subquery("last")
    return select(func.coalesce(func.json_agg(aggregate_order_by(
        func.json_build_array(last.c.n, last.c.at, last.c.key), last.c.n.desc())),
        literal_column("'[]'::json"))).scalar_subquery().label("j_history")


_SEEN = _seen_columns()
_HISTORY = _history_column()


def days(conn: Connection, save_id: int) -> list[DayRecord]:
    """Every stored day of the save, oldest first."""
    j = save_journal.c
    rows = conn.execute(select(j.day, j.notes, j.gap, j.marks, j.through).where(j.save_id == save_id).order_by(j.day))
    return [DayRecord(day=r.day, notes=r.notes, gap=r.gap, marks=r.marks, through=r.through) for r in rows]


def lines_of(conn: Connection, save_id: int, keys: Sequence[str], before: int) -> list[tuple[int, str]]:
    """The save's lines, (game second, key), carrying one of `keys` at a game time before `before`, in order."""
    c = save_lines.c
    rows = conn.execute(select(c.at, c.key).where(c.save_id == save_id, c.key.in_(keys), c.at < before)
                        .order_by(c.n))
    return [(r.at, r.key) for r in rows]

