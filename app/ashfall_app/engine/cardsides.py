"""Which stores a card makes (its flows and outcome stores) and which it costs (its flows, inputs and drains). A leaf:
it imports only card data, so rule validation can use it. One store is on at most one side of a card (validation)."""
from .cards import CardDef
from .fightlines import fight_costs, fight_makes
from .ids import StoreId


def card_makes(card: CardDef) -> frozenset[StoreId]:
    fought = () if card.fight is None else fight_makes(card.fight)
    return frozenset(f.store for f in card.makes) | frozenset(a.store for a in (*card.outcome.stores, *fought))


def card_costs(card: CardDef) -> frozenset[StoreId]:
    fought = () if card.fight is None else fight_costs(card.fight)
    return frozenset(f.store for f in card.costs) | frozenset(a.store for a in (*card.inputs, *card.drains, *fought))
