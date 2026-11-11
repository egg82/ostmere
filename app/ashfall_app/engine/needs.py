"""Which of a card's requires its needs list (View.needs) can show: a store held at some level."""
from .ids import StoreId
from .orders import AtLeast, Condition, StoreValue


def store_need(cond: Condition) -> tuple[StoreId, int] | None:
    """The store and level a require asks for, or None when it asks for anything else (a skill level, a card's
    completions, an unlock): those have no entry in the needs list."""
    if isinstance(cond, AtLeast) and isinstance(cond.subject, StoreValue):
        return cond.subject.store, cond.value
    return None
