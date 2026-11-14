"""A store's entry: each thing the game counts, its cap, and whether the player sees it."""
from typing import Literal

from pydantic import Field

from .entries import Entry


class StoreEntry(Entry):
    id: str
    label_key: str
    cap_items: int = Field(ge=1)
    initial_items: int = Field(default=0, ge=0)
    tally: bool = False
    """A count the game keeps and no card spends (arrivals): only an outcome adds to it, a gate reads it, and no card
    takes it as a cost or an input (tally_checks.py)."""
    hidden: bool = False
    """The engine's bookkeeping (a clock, a countdown) the player never sees: no ledger line, in no served figure
    (api/CONTRACT.txt, StoreInfo.hidden)."""
    clock: Literal["dawn", "day", "evening", "night"] | None = None
    """The part of the story's day this store counts through: a clock the player is never shown, made only by standing
    actions, whose conditions read as that time of day (api/CONTRACT.txt, StoreInfo.clock; opening/face_checks.py)."""
