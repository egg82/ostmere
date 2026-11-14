"""One game day composed (the contract in `saves/journal.py`): a gap, a blank, or the day's notes in page order."""
from collections.abc import Sequence

from ..journal import DAY_S, ComposedDay, Gap, Habits, Line, Subject, roll
from .bag import note
from .history import History, away, read, showing
from .ledger import settledness
from .numbers import budget, diligence
from .owed import catchups, corrections, lates
from .own import Candidate, candidates


def compose(save_id: int, day: int, lines: Sequence[Line], composed: Sequence[ComposedDay],
            subjects: Sequence[Subject], habits: Habits) -> ComposedDay:
    _refuse(day, lines, composed)
    history = read(lines, subjects)
    settled = settledness(composed, subjects, habits)
    room = budget(settled, habits)
    gap = _gap(history, subjects, day, room, habits)
    if gap is not None:
        return ComposedDay(day, (), gap)
    caught = catchups(composed, history, subjects)
    fixes = corrections(composed, subjects, habits, day)
    own = candidates(save_id, day, history, composed, subjects, habits, {t.subject for t in caught})
    musts = sorted((c for c in own if c.must), key=lambda c: (c.order, c.telling.subject))
    passing = _passing(save_id, day, own, diligence(settled, habits))
    left = max(0, room - len(caught) - len(musts) - len(fixes))
    kept = sorted(passing, key=lambda c: (-c.care, c.order, c.telling.subject))[:left]
    head = [*caught, *(c.telling for c in musts), *(c.telling for c in kept)]
    if not head and not fixes:
        return ComposedDay(day, (), None)
    told = [*head, *lates(save_id, composed, subjects, habits), *fixes]
    return ComposedDay(day, tuple(note(save_id, composed, t) for t in told), None)


def _refuse(day: int, lines: Sequence[Line], composed: Sequence[ComposedDay]) -> None:
    if any(line.at >= (day + 1) * DAY_S for line in lines):
        raise ValueError(f"journal: a line is at or past the end of day {day}")
    if [r.day for r in composed] != list(range(day)):
        raise ValueError(f"journal: composed is not exactly days 0 .. {day - 1}")


def _gap(history: History, subjects: Sequence[Subject], day: int, room: int, habits: Habits) -> Gap | None:
    if away(history, subjects, day):
        return "away"
    if len(showing(history, subjects, day)) > habits.busy_ratio * room:
        return "busy"
    return None


def _passing(save_id: int, day: int, own: list[Candidate], diligent: float) -> list[Candidate]:
    """The non-musts whose write roll falls under care times diligence (statement 11)."""
    return [c for c in own if not c.must and roll(save_id, day, c.telling.subject, "write") < c.care * diligent]
