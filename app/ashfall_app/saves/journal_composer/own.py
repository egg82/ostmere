"""A subject weighed at one of its moments: how it is told, whether it is a must, and its care (statements 7, 8, 10 and
17)."""
from dataclasses import dataclass

from ..journal import Habits, Subject, roll
from .history import History, run
from .numbers import faded, pressed
from .telling import Telling, band, is_must, own_slot, plain


@dataclass(frozen=True)
class Candidate:
    """A subject with a slot to tell it by."""

    telling: Telling
    must: bool
    care: float


def candidate(save_id: int, day: int, s: Subject, told: int, history: History, habits: Habits,
              change: bool) -> Candidate | None:
    """`told`: its tellings before this moment, a catch-up today among them (statement 9). `change`: the moment brings a
    key the subject never held, so `w` counts as 0 (statement 10)."""
    t = _telling(save_id, day, s, told, history, habits)
    if t is None:
        return None
    must = is_must(s, told)
    return Candidate(t, must, 1.0 if must else _care(s, told, day, history, habits, change))


def _telling(save_id: int, day: int, s: Subject, told: int, history: History, habits: Habits) -> Telling | None:
    slot = own_slot(s, told)
    if slot == "mention":
        b = band(s, len(history.keys(s.id, day)))
        return Telling(s.id, "mention", b.keys, f"mention.{b.at_least}") if b is not None and b.keys else None
    if slot == "first" and s.misremember and s.correction:
        if roll(save_id, day, s.id, "misremember") < habits.misremember_rate:
            return plain(s, "misremember")
    return plain(s, slot) if slot is not None else None


def _care(s: Subject, told: int, day: int, history: History, habits: Habits, change: bool) -> float:
    if s.kind == "worry":
        return pressed(habits.worry, run(history, s.id, day))
    fade = habits.crowd if s.kind == "crowd" else habits.routine
    return faded(fade, 0 if change else told)
