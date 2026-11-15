"""A stored day's notes in page order (statement 18), for days stored before the composer placed notes by their lines.
Only a permutation: no note is added, dropped or redrawn, so history is not recomposed (statement 20)."""
from collections.abc import Sequence

from ..journal import ComposedDay, Note, Subject
from .history import History, showing
from .ledger import gap_run

_UNKNOWN = 1 << 62


def page_order(day: ComposedDay, before: Sequence[ComposedDay], history: History,
               subjects: Sequence[Subject]) -> ComposedDay:
    """`day` with its notes in statement 18's order. `before` is the stored days 0 .. day - 1. A note whose subject no
    longer shows (a retired line, a removed subject) keeps its place among the notes of its group, after the placed."""
    ran = {s.id: min(history.first_at(s.id, d) for d in gap_run(before) if history.shows(s.id, d))
           for d in gap_run(before) for s in showing(history, subjects, d)}
    notes = sorted(day.notes, key=lambda n: _key(n, day.day, history, ran))
    return ComposedDay(day.day, tuple(notes), day.gap, day.marks)


def _key(note: Note, day: int, history: History, ran: dict[str, int]) -> tuple[int, int, str]:
    if note.slot == "catchup":
        return 0, ran.get(note.subject, _UNKNOWN), note.subject
    if note.slot == "late":
        return 2, 0, note.subject
    if note.slot == "correction":
        return 3, 0, note.subject
    return 1, history.first_at(note.subject, day) if history.shows(note.subject, day) else _UNKNOWN, note.subject
