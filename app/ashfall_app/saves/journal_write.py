"""The journal's days composed in a step's transaction (docs/design/journal.md, "What it reads, and when it writes"): a
game day is composed by the first step whose save time passes its end, from the stored days and the save's lines
before that end, so composing a day live or on a return is one path, and a save with no days stored composes every day
it has closed. The step's statement stores them (db/step.py)."""
from bisect import bisect_left
from collections.abc import Sequence

from sqlalchemy import Connection

from .. import engine as e
from ..db import journal as rows
from ..db.saves import SaveRecord
from ..db.step import JournalDay
from .interface import Ruleset
from .journal_composer.history import read
from .journal_composer.order import page_order
from .journal import DAY_S, MARK_KINDS, ComposedDay, Line, Note, compose_day
from .journal_rules import JournalRules


def keys(rs: Ruleset) -> list[str]:
    """The line keys a stored line may carry and feed a subject: the subjects' keys, and the keys renamed into them."""
    j = rs.journal
    if j is None:
        return []
    return sorted({*j.sources, *(old for old, new in rs.line_renames.items() if new in j.sources)})


def composed(conn: Connection, row: SaveRecord, seen: rows.Seen | None, lines: Sequence[e.Line], time: int,
             rs: Ruleset) -> tuple[ComposedDay, ...]:
    """The days a step leaving the save at game time `time` composes, oldest first: every day whose end is at or before
    `time`, from the one after the newest stored. `seen` is what the save's locking statement read of its journal
    (db/journal.py `locked`); `lines` are the step's own, not yet stored. When that read was not fresh (the lock waited
    on another write), or did not read the days, they are read again here under the lock, so a step that waited on
    another, or runs again after a failover, starts after the days that one stored."""
    j, closed = rs.journal, time // DAY_S
    if j is None or seen is None or seen.next_day >= closed:
        return ()
    if seen.fresh and seen.days is not None and seen.lines is not None:
        found, keyed = seen.days, seen.lines
    else:
        found, keyed = rows.days(conn, row.id), rows.lines_of(conn, row.id, keys(rs), closed * DAY_S)
    stored = tuple(day_of(r) for r in found)
    if len(stored) >= closed:
        return ()
    history = fed([*keyed, *((ln.time, str(ln.key)) for ln in lines)], rs, j)
    ats = [ln.at for ln in history]
    days = list(stored)
    for d in range(len(stored), closed):
        upto = tuple(history[:bisect_left(ats, (d + 1) * DAY_S)])
        days.append(compose_day(row.id, d, upto, tuple(days), j.subjects, j.habits))
    return tuple(days[len(stored):])


def day_of(r: rows.DayRecord) -> ComposedDay:
    return ComposedDay(r.day, tuple(Note(n["subject"], n["slot"], n["key"]) for n in r.notes),
                       "busy" if r.gap == "busy" else "away" if r.gap == "away" else None,
                       tuple(k for k in MARK_KINDS if k in r.marks))


def stored_form(d: ComposedDay) -> JournalDay:
    return JournalDay(d.day, [{"subject": n.subject, "slot": n.slot, "key": n.key} for n in d.notes], d.gap,
                      list(d.marks))


def fed(pairs: Sequence[tuple[int, str]], rs: Ruleset, j: JournalRules) -> list[Line]:
    """The lines, (game second, key), as the composer reads them: renamed, retired ones dropped, one per source."""
    return sorted((Line(key, at, source) for at, old in pairs if (key := rs.line_renames.get(old, old)) not in rs.retired_lines
                   for source in j.sources.get(key, ())), key=lambda ln: ln.at)


def written(conn: Connection, save_id: int, rs: Ruleset) -> tuple[ComposedDay, ...]:
    """The save's stored days that have notes, oldest first, each in page order (statement 18): a day stored before the
    composer ordered its notes by their lines is read in that order, its rows untouched."""
    stored = [day_of(r) for r in rows.days(conn, save_id)]
    j = rs.journal
    if j is None or not any(d.notes for d in stored):
        return tuple(d for d in stored if d.notes)
    history = read(fed(rows.lines_of(conn, save_id, keys(rs), len(stored) * DAY_S), rs, j), j.subjects)
    return tuple(page_order(d, stored[:d.day], history, j.subjects) for d in stored if d.notes)
