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
from .journal import DAY_S, MARK_KINDS, ComposedDay, Line, Note, compose_day
from .journal_rules import JournalRules
from .journal_tallies import Tallies

_log = logging.getLogger(__name__)


def keys(rs: Ruleset) -> list[str]:
    """The line keys a stored line may carry and feed a subject: the subjects' keys."""
    j = rs.journal
    if j is None:
        return []
    return sorted(j.sources)


def composed(conn: Connection, row: SaveRecord, seen: rows.Seen | None, lines: Sequence[e.Line], began: e.Save,
             after: e.Save, rs: Ruleset) -> tuple[tuple[ComposedDay, ...], list[JournalDay]]:
    """The days a step from `began` to `after` (game time `time`) adds notes to, as they now stand, oldest first; and
    what it stores. `seen` is what the save's locking statement read of its journal (db/journal.py `locked`); `lines`
    are the step's own, not yet stored; the loss runners' tallies at each day's end are read between the two saves. When that read was not fresh (the lock waited on another write), the days and lines are
    read again here under the lock, so a step that waited on another, or runs again after a failover, extends what that
    one stored."""
    j, time = rs.journal, after.time
    if j is None or seen is None:
        return (), []
    tallies = Tallies(began, after, rs.rules, j.losses)
    if seen.fresh:
        found, keyed = seen.days, seen.lines
    else:
        found, keyed = rows.days(conn, row.id), rows.lines_of(conn, row.id, keys(rs), time + 1)
    history = fed([*keyed, *((ln.time, str(ln.key)) for ln in lines)], j)
    history = history[:bisect_right([ln.at for ln in history], time)]
    stored = [day_of(r) for r in found]
    start = len(stored) - (1 if found and _open(found[-1]) else 0)
    days = stored[:start]
    served: list[ComposedDay] = []
    store: list[JournalDay] = []
    for d in range(start, time // DAY_S + 1):
        end = (d + 1) * DAY_S
        page = compose_day(row.id, d, tuple(ln for ln in history if ln.at < end), tuple(days), j.subjects, j.habits,
                           ended=time >= end, losses=tallies.at(end) if time >= end else ())
        now, added = _extended(row.id, stored[d] if d < len(stored) else None, page, min(time, end))
        days.append(now)
        if added is not None:
            store.append(added)
            if added.notes:
                served.append(now)
    return tuple(served), store


def _open(r: rows.DayRecord) -> bool:
    return r.through < (r.day + 1) * DAY_S


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
    return ComposedDay(r.day, tuple(Note(n["subject"], n["slot"], n["key"], n.get("count")) for n in r.notes),
                       "busy" if r.gap == "busy" else "away" if r.gap == "away" else None,
                       tuple(k for m in r.marks for k in MARK_KINDS if k == m))


def stored_form(d: ComposedDay, through: int) -> JournalDay:
    return JournalDay(d.day, [{"subject": n.subject, "slot": n.slot, "key": n.key,
                               **({} if n.count is None else {"count": n.count})} for n in d.notes], d.gap,
                      list(d.marks), through)


def fed(pairs: Sequence[tuple[int, str]], j: JournalRules) -> list[Line]:
    """The lines, (game second, key), as the composer reads them: one per source, by game second and, within one, in
    the order given."""
    return sorted((Line(key, at, source) for at, key in pairs for source in j.sources.get(key, ())), key=lambda ln: ln.at)


def written(conn: Connection, save_id: int, seen: rows.Seen | None) -> tuple[ComposedDay, ...]:
    """The save's stored days that have notes, oldest first, as stored. The days are `seen`'s when the locking statement
    read them fresh, read again otherwise."""
    found = seen.days if seen is not None and seen.fresh else rows.days(conn, save_id)
    return tuple(d for d in map(day_of, found) if d.notes)
