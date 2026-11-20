"""A modifier's change as a text's {pct} slot is filled from it."""
from .. import engine as e
from ..opening.entries import ModifierEntry


def changes(mods: list[ModifierEntry]) -> list[int]:
    """The modifiers' signed changes in basis points (a multiplier of 11000 is +1000, an addition of 5000 is +5000),
    each distinct value once in authored order: what a text's {pct} and {pct_b} slots are filled from."""
    return list(dict.fromkeys(m.amount_bp - (e.BP if m.kind == "mul_bp" else 0) for m in mods))
