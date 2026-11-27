"""Wire model of the stores' rates as set (View.store_rows; contract/store-rows.txt, "Store rows"); the conventions in models.py
hold here."""
from enum import StrEnum

from pydantic import BaseModel


class Heading(StrEnum):
    EMPTIES = "empties"
    FILLS = "fills"
    STEADY = "steady"


class StoreRow(BaseModel):
    """One ledger store under the setup as set: its net per hour with every runner counted, and where that takes it."""

    store: str
    per_hour: int
    """The store's net per hour as set, rate units, unclamped (the ledger's net_per_hour with a tap of the hands set
    aside, as goal_rows are)."""
    heading: Heading
    """empties: the net is below 0 and the store holds something; fills: above 0 and it is under its cap; steady:
    otherwise (a store already at 0 and falling is empties at `at` = now)."""
    at: int | None
    """Game time the store reaches 0 (empties) or its cap (fills) if the rates as set hold; null when steady."""
    mixed: bool
    """A card of the hands' mix makes or costs the store: under a dry run of an edit, the edit's own stores."""
