"""A day's page marks (statement 21): the kinds a note holds as it is written, each drawn under its rate, the first
`marks_most` drawn kept."""
from collections.abc import Mapping

from ..journal import Habits, MarkKind, Note, Subject, roll

ABOUT_ANOTHER_DAY = frozenset({"late", "correction"})


def held(note: Note, subjects: Mapping[str, Subject]) -> list[MarkKind]:
    """The kinds `note` holds: its subject's mark, then `smudge` for a catch-up; none for a late addition or correction."""
    if note.slot in ABOUT_ANOTHER_DAY:
        return []
    s = subjects.get(note.subject)
    own: list[MarkKind] = [s.mark] if s is not None and s.mark is not None else []
    return [*own, "smudge"] if note.slot == "catchup" else own


def drawn(save_id: int, day: int, note: Note, subjects: Mapping[str, Subject], habits: Habits,
          have: list[MarkKind]) -> list[MarkKind]:
    """The kinds `note` adds to a page already carrying `have`."""
    out: list[MarkKind] = []
    for kind in held(note, subjects):
        if kind in have or kind in out or len(have) + len(out) >= habits.marks_most:
            continue
        if roll(save_id, day, kind, "mark") < getattr(habits.marks, kind):
            out.append(kind)
    return out
