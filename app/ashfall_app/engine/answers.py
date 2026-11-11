"""The verb that answers an offer. Semantics: DESIGN.txt, "AnswerOffer"; its effect: answering.py."""
from dataclasses import dataclass

from .ids import AnswerId, KindId, OfferId, RoleId


@dataclass(frozen=True)
class AnswerOffer:
    """Verb: give `answer` to `offer`. It can act when `answer` is one of the offer's answers and the offer is open
    (shown, not answered). From the player: an unknown offer, an answer not of that offer, an offer not shown, or one
    already answered raises InvalidVerbError. Applying it adds Unlock(ANSWERED, offer) and Unlock(ANSWER, answer), lands
    the answer's outcome as a trigger's lands, and orders and the queue evaluate at once."""

    offer: OfferId
    answer: AnswerId


@dataclass(frozen=True)
class AnswerKind:
    """Order verb: answer the first open offer of `kind` (rules order) with its answer of `role`. It can act while an
    offer of the kind is open (shown, not answered), applies that AnswerOffer, and is never dead: it answers each later
    offer of the kind as it shows. Not the player's (decide raises InvalidVerbError) and not a queue entry's. DESIGN.txt,
    "OFFER KINDS"."""

    kind: KindId
    role: RoleId
