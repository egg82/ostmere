"""Offers: someone asks the player something, with two or more answers. Type Objects only; their state is three
only-growing unlocks (shown, answered, which answer). Semantics: DESIGN.txt, "Offers"."""
from dataclasses import dataclass

from .cards import Outcome
from .ids import AnswerId, KindId, OfferId, RoleId


@dataclass(frozen=True)
class AnswerDef:
    """One answer: what lands when it is given, as a trigger's outcome lands."""

    id: AnswerId
    outcome: Outcome = Outcome()
    role: RoleId | None = None
    """What this answer means in its offer's kind (DESIGN.txt, "OFFER KINDS"); set exactly when the offer has a kind."""


@dataclass(frozen=True)
class OfferDef:
    """An offer and its answers, in the order the page shows them (two or more; answer ids unique across offers).
    What shows it is an ordinary trigger whose outcome unlocks it (the loader makes one per offer)."""

    id: OfferId
    answers: tuple[AnswerDef, ...]
    kind: KindId | None = None
    """The group of offers this one belongs to; every offer of a kind has the same roles."""
