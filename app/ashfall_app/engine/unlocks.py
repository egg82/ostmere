"""The unlock set: what the player can see and use, as engine state, so the client never decides it.

Semantics: DESIGN.txt, "Unlocks".
"""
from dataclasses import dataclass
from enum import Enum


class UnlockKind(Enum):
    ACTION = "action"
    """A standing action."""
    CARD = "card"
    SKILL = "skill"
    STORE = "store"
    CHIP = "chip"
    FEATURE = "feature"
    RETIRED = "retired"
    """A card a newer one replaced (a tool upgrade): out of play like a completed card, and every mix holding it
    greys. The id is a card's. Unlocks only grow, so a retirement is never undone (DESIGN.txt, "Retired")."""
    OFFER = "offer"
    """An offer shown (its id an OfferId): open until it is answered, and it never expires (DESIGN.txt, "Offers")."""
    ANSWERED = "answered"
    """An offer answered, by either answer (its id the OfferId). Only an applied AnswerOffer adds it, and it counts
    only where save.unlocked holds it, whatever rules.opening is."""
    ANSWER = "answer"
    """The answer given (its id an AnswerId); added with ANSWERED, and held the same way."""
    ENTRY = "entry"
    """A journal page written (its id an EntryId): an ordinary kind, the engine never reads it (DESIGN.txt, "Unlocks")."""
    NOTE = "note"
    """A note written on a journal page (its id a NoteId); as ENTRY."""
    JOINED = "joined"
    """A ruled lane's person has joined (its id a LaneId): added by an Outcome.joins part alone, held the same way as
    ANSWERED, and only ever growing (DESIGN.txt, "THE TOWN'S MIX")."""
    LEFT = "left"
    """A ruled lane's person has left the town (its id a LaneId): added by an Outcome.leaves part alone, held as JOINED
    is; the lane's cards are out of play from then on (DESIGN.txt, "LEAVES")."""


@dataclass(frozen=True)
class Unlock:
    """One id of one kind made visible and usable. `id` is the typed id of that kind (ActionId, FeatureId, ...).

    Save.unlocked is sorted by unlock_key, so two saves with the same set compare equal.
    """

    kind: UnlockKind
    id: str


PRESENT_ONLY = frozenset({UnlockKind.ANSWERED, UnlockKind.ANSWER, UnlockKind.JOINED, UnlockKind.LEFT})
"""The kinds that count only when the save holds them, even with rules.opening None (DESIGN.txt, "Offers", "THE
TOWN'S MIX")."""


def unlock_key(u: Unlock) -> tuple[str, str]:
    """The canonical sort key of the unlock set: (kind.value, id)."""
    return (u.kind.value, u.id)
