"""Which stores a runner makes and which it costs: a standing action's flows, or a card's (cardsides)."""
from .cardsides import card_costs, card_makes
from .fightlines import fight_costs, fight_makes
from .ids import ActionId, CardId, Runner, StoreId
from .index import derived, index
from .rules import Rules


def makes(rules: Rules, runner: Runner) -> frozenset[StoreId]:
    return derived(rules, "_makes", _all_makes)[runner]


def costs(rules: Rules, runner: Runner) -> frozenset[StoreId]:
    return derived(rules, "_costs", _all_costs)[runner]


def touching(rules: Rules, store: StoreId) -> frozenset[Runner]:
    """The runners that make or cost `store`."""
    return derived(rules, "_touching", _all_touching).get(store, frozenset())


def _runners(rules: Rules) -> list[Runner]:
    return [*(a.id for a in rules.standing), *(c.id for c in rules.cards)]


def _all_makes(rules: Rules) -> dict[Runner, frozenset[StoreId]]:
    return {r: _makes(rules, r) for r in _runners(rules)}


def _all_costs(rules: Rules) -> dict[Runner, frozenset[StoreId]]:
    return {r: _costs(rules, r) for r in _runners(rules)}


def _all_touching(rules: Rules) -> dict[StoreId, frozenset[Runner]]:
    out: dict[StoreId, set[Runner]] = {}
    for r in _runners(rules):
        for st in _makes(rules, r) | _costs(rules, r):
            out.setdefault(st, set()).add(r)
    return {st: frozenset(rs) for st, rs in out.items()}


def _makes(rules: Rules, runner: Runner) -> frozenset[StoreId]:
    ix = index(rules)
    card = ix.cards.get(CardId(runner))
    if card is not None:
        return card_makes(card)
    a = ix.standing[ActionId(runner)]
    return frozenset(f.store for f in a.makes) | frozenset(x.store for x in (fight_makes(a.fight) if a.fight else ()))


def _costs(rules: Rules, runner: Runner) -> frozenset[StoreId]:
    ix = index(rules)
    card = ix.cards.get(CardId(runner))
    if card is not None:
        return card_costs(card)
    a = ix.standing[ActionId(runner)]
    return frozenset(f.store for f in a.costs) | frozenset(x.store for x in (fight_costs(a.fight) if a.fight else ()))
