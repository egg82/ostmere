"""Wire models of what a card requires (CardInfo.skill_needs, step_needs) and what holds it back (Card.blocker,
needs); the conventions in models.py hold here."""
from pydantic import BaseModel

from .decision_models import Condition, Segment


class SkillNeed(BaseModel):
    """A level a card requires of a skill: listed on the card as ui.card.needs_skill, short while below it."""

    skill: str
    level: int


class StepNeed(BaseModel):
    """A step a card requires: another card's completions, listed as ui.card.needs_step, short while below `count`."""

    card: str
    count: int


class Blocker(BaseModel):
    """The first unmet precondition, as the condition that would make it ready; ready_at null: not by itself."""

    condition: Condition
    ready_at: int | None


class Need(BaseModel):
    """A store a tap of the card needs. quantity: the most its input or any requirement on that store's value asks;
    segment: how much there is, sampled like a ledger line's (served for a locked store too).
    Drawn short while the sample is below quantity; whether the card is ready is still its blocker's to say. gate: drawn
    in its place while set, the store unnamed (CONTRACT.txt, "Cards"); makers: the cards and standing actions in play
    that make the store; spent: drawn as used up, set while short, nothing in play can make the store again and every
    trigger that grants it has fired."""

    store: str
    quantity: int
    segment: Segment
    gate: Condition | None
    makers: list[str]
    spent: bool
