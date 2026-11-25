"""Wire model of a store as the content serves it (Content.store_infos); the conventions in models.py hold here."""
from typing import Literal

from pydantic import BaseModel


class StoreInfo(BaseModel):
    store: str
    label_key: str
    cap: int
    """The cap a new game starts with; LedgerLine.cap is the cap now."""
    made_by: list[str]
    """The cards that make it, in card order: by what a completion lands or a make flow, or by training the skill
    whose level pays it, or by the completion a find waits on."""
    hidden: bool
    """The engine's bookkeeping (a clock, a countdown), never seen: no ledger line, in no served figure (AnswerInfo.gains)."""
    tally: bool
    """A count the game keeps (arrivals): no ledger line, but a card's need on it is drawn as have/need."""
    clock: Literal["dawn", "day", "evening", "night"] | None
    """The part of the story's day this clock counts through: a condition on it reads as that time (ui.when.*), never as
    an amount (CONTRACT.txt, "Cards", "Line causes")."""
    rises_in_steps: bool
    """Nothing that runs raises it (no card lands or flows it, no standing action flows it): only an event adds to it, a
    step at a time, so a rule on it cannot flip at one level on a flow and the page builds one with no band
    (CONTRACT.txt, "a store rule")."""
    bonus_bp: int | None
    """Set on a store only eaters take from (standing actions, or a station's cards that take and make nothing), each
    holding a lane speed while it runs: that speed change, in basis points. Its ledger line is a bonus, never red, and
    says the bonus is off once dry (CONTRACT.txt, "Ledger")."""
    group_key: str | None
    """The label of the one ledger row this store shares with the stores of the same key, which opens on a tap to show
    each (CONTRACT.txt, "Ledger"); null: a row of its own."""
