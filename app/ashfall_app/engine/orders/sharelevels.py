"""Share levels: a store condition's level given as basis points of the store's cap, read as a quantity off the cap at
the instant the condition is read. design/share-levels.txt, "SHARE LEVELS" (the reading table and the band of one item)."""
from ..unlocks.gates import store_cap
from .orders import AtLeast, AtMost, StoreValue
from ..core.rules import Rules
from ..core.state import Save
from ..core.units import BP, QUANTITY_SCALE, ceil_div

Q = QUANTITY_SCALE


def read_levels(save: Save, rules: Rules, cond: AtLeast | AtMost) -> AtLeast | AtMost:
    """`cond` with each share level replaced by the quantity it reads under the cap now, and the band kept one item wide
    within the store's range; `cond` itself when it holds no share level."""
    if not (cond.value_of_cap or cond.release_of_cap) or not isinstance(cond.subject, StoreValue):
        return cond
    whole = store_cap(save, rules, cond.subject.store) // Q
    at_most = isinstance(cond, AtMost)
    value = _quantity(cond.value, whole, at_most, at_most) if cond.value_of_cap else cond.value
    release = _quantity(cond.release, whole, at_most, not at_most) if cond.release_of_cap else cond.release
    if at_most:
        return AtMost(cond.subject, value, max(release, value, min(value + Q, whole * Q - 1)))
    return AtLeast(cond.subject, value, min(release, value, max(value - Q, Q)))


def _quantity(b: int, whole: int, at_most: bool, floor_side: bool) -> int:
    """The quantity a share b of `whole` items reads as. The floor side (an at_most's value, an at_least's release)
    holds while the shown items are at or under the share; the other side is reached once they are at or over it. An
    at_most compares with <=, so its quantities sit one unit under the next whole item."""
    items = b * whole // BP + 1 if floor_side else ceil_div(b * whole, BP)
    return items * Q - (1 if at_most else 0)
