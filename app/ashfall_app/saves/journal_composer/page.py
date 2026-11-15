"""The page of the day being composed: its notes and marks as they are written, and its gap once it breaks off. Notes
and marks are only appended (statement 22)."""
from collections.abc import Sequence
from dataclasses import dataclass, field

from ..journal import ComposedDay, Gap, Habits, MarkKind, Note, Subject
from .bag import note
from .ledger import TELLINGS, tellings
from .marks import drawn
from .telling import Telling

OWN = frozenset({"first", "repeat", "misremember", "mention"})


@dataclass
class Page:
    save_id: int
    day: int
    composed: Sequence[ComposedDay]
    subjects: dict[str, Subject]
    habits: Habits
    notes: list[Note] = field(default_factory=list[Note])
    marks: list[MarkKind] = field(default_factory=list[MarkKind])
    gap: Gap | None = None
    shown: set[str] = field(default_factory=set[str])
    """The subjects the day has shown so far (statement 14)."""

    def write(self, t: Telling) -> None:
        n = note(self.save_id, [*self.composed, self.done()], t)
        self.notes.append(n)
        self.marks += drawn(self.save_id, self.day, n, self.subjects, self.habits, self.marks)

    def told(self, subject: str) -> int:
        """`w(S)` before this moment: its tellings in `composed` and on the page so far."""
        return tellings(self.composed, subject) + sum(1 for n in self.notes if n.subject == subject and n.slot in TELLINGS)

    def has_own(self, subject: str) -> bool:
        return any(n.subject == subject and n.slot in OWN for n in self.notes)

    def done(self) -> ComposedDay:
        return ComposedDay(self.day, tuple(self.notes), self.gap, tuple(self.marks))
