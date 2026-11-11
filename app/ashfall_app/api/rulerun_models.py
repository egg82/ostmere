"""What the rules did lately, on the wire (CONTRACT.txt, "Rule runs"; re-exported from models.py)."""
from typing import Literal

from pydantic import BaseModel

from .content_models import Amount
from .decision_models import Order


class RuleRun(BaseModel):
    """One rule's entry: how many times it came on since its entry began, its last start and its last let-go (null
    until it has let go), each with the amount of the store its condition reads (null for a condition on no store).
    `order` is the rule as the save has it now: equal to one of View.orders, unless `ended` is set: the game removed
    the rule, at a season's turn or when its person left, at off_at. on_at is null only on an ended rule that never
    came on. `ended` "stint" is a goal stint that popped at its goal (CONTRACT.txt, "Rule runs"): `order` is
    {when: its until, then: its switch_mix}, on_at when its mix began to run (null if the goal held as it came to
    control), off_at when its goal landed. `made`, on an ended stint only: what the save gained, from on_at to off_at,
    in the stores its mix's cards make, the goal's store first, then the largest, at most two; [] otherwise."""

    order: Order
    starts: int
    on_at: int | None
    on_level: int | None
    off_at: int | None
    off_level: int | None
    ended: Literal["season", "left", "stint"] | None
    made: list[Amount]
