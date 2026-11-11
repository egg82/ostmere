"""A card's requires, read off the save: which one is false now."""
from .cards import CardDef
from .rules import Rules
from .state import Save


def first_unmet(save: Save, rules: Rules, card: CardDef) -> int | None:
    """The index in card.requires of the first condition that is false now, or None when they all hold."""
    from .conditions import is_true  # deferred: conditions -> discrete -> rates -> requires

    return next((i for i, c in enumerate(card.requires) if not is_true(save, rules, c)), None)
