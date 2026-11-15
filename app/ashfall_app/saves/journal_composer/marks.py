"""A day's page marks (statement 21): the kinds its notes hold, each drawn under its rate, the first `marks_most`
kept."""
from collections.abc import Sequence

from ..journal import MARK_KINDS, Habits, MarkKind, Note, Subject, roll

ABOUT_ANOTHER_DAY = frozenset({"late", "correction"})


def marks(save_id: int, day: int, notes: Sequence[Note], subjects: Sequence[Subject],
          habits: Habits) -> tuple[MarkKind, ...]:
    marked: dict[str, MarkKind] = {s.id: s.mark for s in subjects if s.mark is not None}
    held: set[MarkKind] = {marked[n.subject] for n in notes if n.slot not in ABOUT_ANOTHER_DAY and n.subject in marked}
    if any(n.slot == "catchup" for n in notes):
        held.add("smudge")
    drawn: list[MarkKind] = [k for k in MARK_KINDS
                             if k in held and roll(save_id, day, k, "mark") < getattr(habits.marks, k)]
    return tuple(drawn[:habits.marks_most])
