"""The journal's days composed in a step's transaction (docs/design/journal.md, "Written as the day goes"): the day still
being written and each day the step begins are composed from the stored days and the save's lines up to the step's
save time, so a page is the same however the steps fell, and only what the stored row lacks is added to it. A save with
no days stored composes every day it has begun. The step's statement stores them (db/step.py)."""
import logging
from bisect import bisect_right
from collections.abc import Sequence

from sqlalchemy import Connection

from .. import engine as e
from .. import logs
from ..db import journal as rows
from ..db.saves import SaveRecord
from ..db.step import JournalDay
from .interface import Ruleset
from .journal_composer.history import read
from .journal_composer.order import page_order
from .journal import DAY_S, MARK_KINDS, ComposedDay, Line, Note, compose_day
from .journal_rules import JournalRules

_log = logging.getLogger(__name__)


def keys(rs: Ruleset) -> list[str]:
    """The line keys a stored line may carry and feed a subject: the subjects' keys, and the keys renamed into them."""
    j = rs.journal
    if j is None:
        return []
    return sorted({*j.sources, *(old for old, new in rs.line_renames.items() if new in j.sources)})


def composed(conn: Connection, row: SaveRecord, seen: rows.Seen | None, lines: Sequence[e.Line], time: int,
             rs: Ruleset) -> tuple[tuple[ComposedDay, ...], list[JournalDay]]:
    """The days a step leaving the save at game time `time` adds notes to, as they now stand, oldest first; and what it
    stores. `seen` is what the save's locking statement read of its journal (db/journal.py `locked`); `lines` are the
    step's own, not yet stored. When that read was not fresh (the lock waited on another write), the days and lines are
    read again here under the lock, so a step that waited on another, or runs again after a failover, extends what that
    one stored."""
    j = rs.journal
    if j is None or seen is None:
        return (), []
    if seen.fresh:
        found, keyed = seen.days, seen.lines
    else:
        found, keyed = rows.days(conn, row.id), rows.lines_of(conn, row.id, keys(rs), time + 1)
    history = fed([*keyed, *((ln.time, str(ln.key)) for ln in lines)], rs, j)
    history = history[:bisect_right([ln.at for ln in history], time)]
    stored = [day_of(r) for r in found]
    start = len(stored) - (1 if found and _open(found[-1]) else 0)
    days = stored[:start]
    served: list[ComposedDay] = []
    store: list[JournalDay] = []
    for d in range(start, time // DAY_S + 1):
        end = (d + 1) * DAY_S
        page = compose_day(row.id, d, tuple(ln for ln in history if ln.at < end), tuple(days), j.subjects, j.habits,
                           ended=time >= end)
        now, added = _extended(row.id, stored[d] if d < len(stored) else None, page, min(time, end))
        days.append(now)
        if added is not None:
            store.append(added)
            if added.notes:
                served.append(now)
    return tuple(served), store


def _open(r: rows.DayRecord) -> bool:
    return r.through is not None and r.through < (r.day + 1) * DAY_S


def _extended(save_id: int, was: ComposedDay | None, page: ComposedDay,
              through: int) -> tuple[ComposedDay, JournalDay | None]:
    """The day as stored once this step has written it, and what the step stores (None: nothing). A day held that the
    page does not begin with (the habits or slots changed while it was open) keeps its notes and gains nothing more."""
    if was is None:
        return page, stored_form(page, through)
    if page.notes[:len(was.notes)] != was.notes or page.marks[:len(was.marks)] != was.marks or (
            was.gap is not None and page.gap != was.gap):
        logs.warning(_log, "journal.diverged", save=save_id, day=page.day, stored=len(was.notes),
                     composed=len(page.notes))
        return was, JournalDay(page.day, [], None, [], through)
    added = ComposedDay(page.day, page.notes[len(was.notes):], page.gap if was.gap is None else None,
                        page.marks[len(was.marks):])
    if not added.notes and not added.marks and added.gap is None and through < (page.day + 1) * DAY_S:
        return page, None
    return page, stored_form(added, through)


def day_of(r: rows.DayRecord) -> ComposedDay:
    return ComposedDay(r.day, tuple(Note(n["subject"], n["slot"], n["key"]) for n in r.notes),
                       "busy" if r.gap == "busy" else "away" if r.gap == "away" else None,
                       tuple(k for m in r.marks for k in MARK_KINDS if k == m))


def stored_form(d: ComposedDay, through: int) -> JournalDay:
    return JournalDay(d.day, [{"subject": n.subject, "slot": n.slot, "key": n.key} for n in d.notes], d.gap,
                      list(d.marks), through)


def fed(pairs: Sequence[tuple[int, str]], rs: Ruleset, j: JournalRules) -> list[Line]:
    """The lines, (game second, key), as the composer reads them: renamed, retired ones dropped, one per source, by game
    second and, within one, in the order given."""
    return sorted((Line(key, at, source) for at, old in pairs if (key := rs.line_renames.get(old, old)) not in rs.retired_lines
                   for source in j.sources.get(key, ())), key=lambda ln: ln.at)


def written(conn: Connection, save_id: int, seen: rows.Seen | None, rs: Ruleset) -> tuple[ComposedDay, ...]:
    """The save's stored days that have notes, oldest first, each in page order (statement 18): a day stored whole before
    notes were written as the day goes is read in the order of its time, its row untouched. The days are `seen`'s when
    the locking statement read them fresh, read again otherwise."""
    found = seen.days if seen is not None and seen.fresh else rows.days(conn, save_id)
    stored = [day_of(r) for r in found]
    j = rs.journal
    if j is None or not any(d.notes for d, r in zip(stored, found) if r.through is None):
        return tuple(d for d in stored if d.notes)
    history = read(fed(rows.lines_of(conn, save_id, keys(rs), len(stored) * DAY_S), rs, j), j.subjects)
    return tuple(page_order(d, stored[:d.day], history, j.subjects) if r.through is None else d
                 for d, r in zip(stored, found) if d.notes)
