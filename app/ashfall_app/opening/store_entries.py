"""A store's entry: each thing the game counts, its cap, and whether the player sees it."""
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
