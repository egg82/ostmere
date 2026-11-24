"""One game day composed as it goes (the contract in `saves/journal.py`): its start, each of its moments in order, and,
once it has ended, its end, the loss runners' notes last (losses.py). Each step only appends to the page (statement
22)."""
from collections.abc import Sequence

from ..journal import DAY_S, ComposedDay, Habits, Line, Loss, Subject, roll
from . import losses as told_losses
from .history import History, Moment, away, changed, moments, read
from .ledger import settledness
from .numbers import budget, diligence
from .owed import catchups, corrections, lates
from .own import candidate
from .page import Page


def compose(save_id: int, day: int, lines: Sequence[Line], composed: Sequence[ComposedDay],
            subjects: Sequence[Subject], habits: Habits, ended: bool, losses: Sequence[Loss] = ()) -> ComposedDay:
    _refuse(day, lines, composed)
    history = read(lines, subjects)
    page = Page(save_id, day, composed, {s.id: s for s in subjects}, habits)
    if away(history, subjects, day):
        page.gap = "away"
        return page.done()
    for t in catchups(composed, history, subjects):
        page.write(t)
    settled = settledness(composed, subjects, habits)
    room, diligent = budget(settled, habits), diligence(settled, habits)
    crowds: list[Subject] = []
    for m in moments(lines, subjects, day):
        if not _weigh(page, m, history, room, diligent, crowds):
            return page.done()
    if ended:
        _end(page, history, room, diligent, crowds)
        page.notes += told_losses.notes(save_id, composed, page.notes, losses)
    return page.done()


def _refuse(day: int, lines: Sequence[Line], composed: Sequence[ComposedDay]) -> None:
    if any(line.at >= (day + 1) * DAY_S for line in lines):
        raise ValueError(f"journal: a line is at or past the end of day {day}")
    if [r.day for r in composed] != list(range(day)):
        raise ValueError(f"journal: composed is not exactly days 0 .. {day - 1}")


def _weigh(page: Page, m: Moment, history: History, room: int, diligent: float, crowds: list[Subject]) -> bool:
    """One moment (statements 8 and 11-14); False once the day has broken off into a gap."""
    s = m.subject
    if m.first:
        page.shown.add(s.id)
        if s.away_days > 0:
            page.gap = "away"
            return False
        if len(page.shown) > page.habits.busy_ratio * room:
            page.gap = "busy"
            return False
        if s.kind == "crowd":
            crowds.append(s)
    if s.kind == "crowd" or page.has_own(s.id):
        return True
    c = candidate(page.save_id, page.day, s, page.told(s.id), history, page.habits, m.change)
    if c is None or (c.must and not m.first):
        return True
    if c.must or _passes(page, s.id, c.care, diligent, room):
        page.write(c.telling)
    return True


def _passes(page: Page, subject: str, care: float, diligent: float, room: int) -> bool:
    """A non-must's write roll falls under care times diligence, and the page has room (statements 11 and 12)."""
    return roll(page.save_id, page.day, subject, "write") < care * diligent and len(page.notes) < room


def _end(page: Page, history: History, room: int, diligent: float, crowds: list[Subject]) -> None:
    """The day's end: its crowds, by their first lines, then the late additions and the corrections due (statements 16,
    17 and 22)."""
    for s in crowds:
        c = candidate(page.save_id, page.day, s, page.told(s.id), history, page.habits, changed(history, s.id, page.day))
        if c is not None and _passes(page, s.id, c.care, diligent, room):
            page.write(c.telling)
    fixes = corrections(page.composed, list(page.subjects.values()), page.habits, page.day)
    if page.notes or fixes:
        for t in lates(page.save_id, page.composed, list(page.subjects.values()), page.habits):
            page.write(t)
    for t in fixes:
        page.write(t)
