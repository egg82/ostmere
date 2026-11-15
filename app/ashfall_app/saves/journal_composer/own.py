"""The day's own subjects: how each is told, whether it is a must, its care and its order roll (statements 7, 8, 10,
17 and 18)."""
from collections.abc import Sequence
from dataclasses import dataclass

from ..journal import ComposedDay, Habits, Subject, roll
from .history import History, changed, run, showing
from .ledger import tellings
from .numbers import faded, pressed
from .telling import Telling, band, is_must, own_slot, plain


@dataclass(frozen=True)
class Candidate:
    """A subject showing today with a slot to tell it by."""

    telling: Telling
    must: bool
    care: float
    order: float


def candidates(save_id: int, day: int, history: History, composed: Sequence[ComposedDay], subjects: Sequence[Subject],
               habits: Habits, caught: set[str]) -> list[Candidate]:
    """`caught`: the subjects caught up today, each a telling for the rest of the day (statement 9)."""
    out: list[Candidate] = []
    for s in showing(history, subjects, day):
        told = tellings(composed, s.id) + (s.id in caught)
        t = _telling(save_id, day, s, told, history, habits)
        if t is None:
            continue
        must = is_must(s, told)
        care = 1.0 if must else _care(s, told, day, history, habits)
        out.append(Candidate(t, must, care, roll(save_id, day, s.id, "order")))
    return out


def _telling(save_id: int, day: int, s: Subject, told: int, history: History, habits: Habits) -> Telling | None:
    slot = own_slot(s, told)
    if slot == "mention":
        b = band(s, len(history.keys(s.id, day)))
        return Telling(s.id, "mention", b.keys, f"mention.{b.at_least}") if b is not None and b.keys else None
    if slot == "first" and s.misremember and s.correction:
        if roll(save_id, day, s.id, "misremember") < habits.misremember_rate:
            return plain(s, "misremember")
    return plain(s, slot) if slot is not None else None


def _care(s: Subject, told: int, day: int, history: History, habits: Habits) -> float:
    if s.kind == "worry":
        return pressed(habits.worry, run(history, s.id, day))
    fade = habits.crowd if s.kind == "crowd" else habits.routine
    return faded(fade, 0 if changed(history, s.id, day) else told)
