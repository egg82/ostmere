"""Offers on the wire (CONTRACT.txt, "Offers"): what the view serves of each shown offer, and what the content says
of every offer. Re-exported from models.py and content_models.py."""
from pydantic import BaseModel

from .line_models import LineCause


class OfferAnswer(BaseModel):
    answer: str
    card: str | None
    """The card the answer sets running; null for none."""
    takes_s: int | None
    """Seconds one completion of that card would take started now; null without a card."""


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
    """What led to the offer, as a line's cause (CONTRACT.txt, "Line causes"): its gate, or, for a gate the page cannot
    word (a hidden store, a lane's rules), the earlier offer whose answer it requires; null with neither."""
    waiting_key: str | None
    """What waiting costs; null when waiting is free, as usual."""
    expiry_key: str | None
    """When the offer goes unanswered; null when it waits until answered, as usual."""
    permanence_key: str | None
    """What the answer settles for good, for a choice to weigh; null says nothing."""
