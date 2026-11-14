"""The stored days read as given (statement 20): tellings, settledness, the gap run just ended, and a slot's draws."""
from collections.abc import Sequence

from ..journal import ComposedDay, Habits, SlotName, Subject

TELLINGS: frozenset[SlotName] = frozenset({"first", "repeat", "catchup", "misremember", "mention"})


def tellings(composed: Sequence[ComposedDay], subject: str) -> int:
    """`w(S)`: the subject's notes in `composed` by a telling slot."""
    return sum(1 for r in composed for n in r.notes if n.subject == subject and n.slot in TELLINGS)


def settledness(composed: Sequence[ComposedDay], subjects: Sequence[Subject], habits: Habits) -> float:
    beats = {s.id for s in subjects if s.kind == "beat"}
    written = sum(1 for r in composed if r.notes)
    beat_notes = sum(1 for r in composed for n in r.notes if n.subject in beats)
    return max(0.0, written - habits.beat_refresh * beat_notes)


def gap_run(composed: Sequence[ComposedDay]) -> range:
    """The days of the run of stored gaps that ends on the last stored day; empty when that day is no gap."""
    start = len(composed)
    while start > 0 and composed[start - 1].gap is not None:
        start -= 1
    return range(start, len(composed))


def drawn(composed: Sequence[ComposedDay], subject: str, slot: SlotName, keys: tuple[str, ...]) -> list[str]:
    """The keys stored for the subject by `slot`, oldest first, keeping only those `keys` still holds (statement 19)."""
    return [n.key for r in composed for n in r.notes if n.subject == subject and n.slot == slot and n.key in keys]
