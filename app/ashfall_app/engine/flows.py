"""A continuous make or cost of one store, shared by cards and standing actions (cards.py, rules.py)."""
from dataclasses import dataclass

from .ids import StoreId


@dataclass(frozen=True)
class Flow:
    """A make or cost of one store, per hour at a 100% share (per_hour >= 0)."""

    store: StoreId
    per_hour: int
