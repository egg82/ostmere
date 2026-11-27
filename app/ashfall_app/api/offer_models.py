"""Offers on the wire (contract/offers.txt, "Offers"): what the view serves of each shown offer, and what the content says
of every offer. Re-exported from models.py and content_models.py."""
from pydantic import BaseModel

from .line_models import LineCause


class AnswerShift(BaseModel):
    """One lasting change an open offer's answer makes, as the total on its target: `now_bp` today and `after_bp` once
    the answer is given, signed changes in basis points (a +15% total is 1500), as AnswerInfo.change_bp."""

    now_bp: int
    after_bp: int


class OfferAnswer(BaseModel):
    answer: str
    card: str | None
    """The card the answer sets running; null for none."""
    takes_s: int | None
    """Seconds one completion of that card would take started now; null without a card."""
    shifts: list[AnswerShift | None]
    """One per entry of AnswerInfo.change_bp, in its order: that change's target now and after the answer; null where the
    entries of one change aim at targets that stand differently. Empty once the offer is answered."""


class Offer(BaseModel):
    """A shown offer, in content order: `answer` null while it is open, else the answer given."""

    offer: str
    answer: str | None
    answers: list[OfferAnswer]


class AnswerGain(BaseModel):
    store: str
    quantity: int
    """In quantity units, as Amount.quantity."""


class AnswerInfo(BaseModel):
    answer: str
    label_key: str
    cost_key: str
    """The answer's cost, its {d} filled from OfferAnswer.takes_s (left out while that is null), its {pct} and
    {pct_b} from change_bp, its {gain} and {gain_b} from gains."""
    change_bp: list[int]
    """The answer's modifiers as signed changes in basis points, as LevelPays.change_bp. Empty for an answer that
    installs none."""
    gains: list[AnswerGain]
    """The stores the answer puts in, in authored order, one entry per authored store line."""
    role: str | None
    """What the answer means in its offer's kind; null for an offer without one."""


class KindRole(BaseModel):
    role: str
    label_key: str


class OfferKindInfo(BaseModel):
    """What the content says of an offer kind: the label of each role, written for whoever asks, which words the rule
    that answers the kind (an offer's own answer labels are written for that one ask)."""

    kind: str
    roles: list[KindRole]


class OfferInfo(BaseModel):
    offer: str
    text_key: str
    kind: str | None
    """The group of offers that ask the same question, answered together by one rule; null for an unkinded offer."""
    line_keys: list[str]
    """The lines written when the offer shows: its row is revealed after the last of them."""
    answers: list[AnswerInfo]
    askers: list[str]
    """The ruled lanes whose people ask, named by their lane's label; empty when no one person asks."""
    cause: LineCause | None
    """What led to the offer, as a line's cause (contract/endpoints.txt, "Line causes"): its gate, or, for a gate the page cannot
    word (a hidden store, a lane's rules), the earlier offer whose answer it requires; null with neither."""
    waiting_key: str | None
    """What waiting costs; null when waiting is free, as usual."""
    expiry_key: str | None
    """When the offer goes unanswered; null when it waits until answered, as usual."""
    permanence_key: str | None
    """What the answer settles for good, for a choice to weigh; null says nothing."""
