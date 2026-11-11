"""Status chips (cold, hungry, tired) and triggers (content gates that fire once). Both read the order vocabulary.

Semantics: DESIGN.txt, "Chips", "Triggers". What they do: work.py.
"""
from dataclasses import dataclass

from .ids import ChipId, LineKey, TriggerId
from .modifiers import Modifier
from .orders import Condition
from .cards import Outcome


@dataclass(frozen=True)
class ChipDef:
    """A status shown while it is unlocked and its latched condition is true; while shown, `effects` join every rate's
    stack. Each effect's source is the chip's id (validated), so explain() names the chip. Its latch is kept whether
    or not it is unlocked. on_line is emitted the first time it becomes shown in the save (whichever of its latch rising
    and its unlock came second) and never again, off_line each time it stops being shown (DESIGN.txt, "Chips")."""

    id: ChipId
    when: Condition
    effects: tuple[Modifier, ...] = ()
    on_line: LineKey | None = None
    off_line: LineKey | None = None


@dataclass(frozen=True)
class TriggerDef:
    """Fires once per save, at the first instant `when` and every condition in `requires` are true (time 0 included:
    new_save resolves it), applying `outcome` (a cards.Outcome); orders and the queue then evaluate. Each of
    `requires` is on a discrete subject (Unlocked, Running), so it changes only at an instant the pending check sees
    (DESIGN.txt, "Triggers")."""

    id: TriggerId
    when: Condition
    outcome: Outcome
    requires: tuple[Condition, ...] = ()

