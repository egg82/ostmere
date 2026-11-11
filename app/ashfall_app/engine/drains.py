"""Drains: a card's take paid as an input is and forgiven at 0 (DESIGN.txt, "DRAINS"). A leaf of rules_check: the
rules arrive as an argument and are never imported."""
from typing import TYPE_CHECKING

from .cards import CardDef
from .errors import InvalidRulesError
from .fightlines import fight_costs, fight_makes
from .ids import StoreId

if TYPE_CHECKING:
    from .rules import Rules


def check_drains(rules: "Rules", where: str, card: CardDef, listed: list[StoreId]) -> None:
    """InvalidRulesError, naming `where` and the store, for a drain on an unknown store, a quantity below 1, a store
    in `listed` (the card's makes, costs, inputs and outcome stores) or in its fight's lines, or one drained twice."""
    stores = {s.id for s in rules.stores}
    fought = [a.store for a in (*fight_costs(card.fight), *fight_makes(card.fight))] if card.fight else []
    seen: set[StoreId] = set()
    for a in card.drains:
        if a.store not in stores:
            raise InvalidRulesError(f"{where}: a drain names an unknown store {a.store}")
        if a.quantity < 1:
            raise InvalidRulesError(f"{where}: the drain on {a.store} must take at least 1")
        if a.store in listed or a.store in fought:
            raise InvalidRulesError(f"{where}: {a.store} is drained and also on another of the card's lines")
        if a.store in seen:
            raise InvalidRulesError(f"{where}: {a.store} is drained twice")
        seen.add(a.store)
