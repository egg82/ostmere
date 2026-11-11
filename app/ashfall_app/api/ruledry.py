"""View.order_dry: a store rule's mix that is, or may be, short of an input it cannot release without (CONTRACT.txt,
"Dry rules"). The line a goal row names (goalrows.limit) and the rates as set (setrates.py) answer it."""
from .. import engine as e
from ..engine.rates import Running
from ..engine.sides import costs, makes
from . import goal_models as g
from . import goalrows
from . import setrates as sr


def order_dry(save: e.Save, rules: e.Rules, v: e.View) -> list[g.RuleDry | None]:
    """One entry per order: None unless it is a mix rule that releases when a store rises (at_most) on a store."""
    shown = frozenset(ln.store for ln in v.ledger)
    now = sr.as_set(save, rules)
    return [_dry(save, rules, now, shown, o, state) for o, state in zip(save.orders, v.order_states)]


def _dry(save: e.Save, rules: e.Rules, now: Running, shown: frozenset[e.StoreId], order: e.Order,
         state: e.OrderState) -> g.RuleDry | None:
    when, then = order.when, order.then
    if not (isinstance(when, e.AtMost) and isinstance(when.subject, e.StoreValue) and isinstance(then, e.SwitchMix)):
        return None
    store = when.subject.store
    if state is e.OrderState.ON and sr.net_per_hour(save, rules, now, store) <= 0:
        dry = goalrows.limit(save, rules, now, sr.movers(rules, now, store, None), shown)
        if dry is not None:
            return g.RuleDry(store=dry.store, holding=True)
    return _unfed(rules, shown, e.flatten_shares(save.mixes, then.mix), store)


def _unfed(rules: e.Rules, shown: frozenset[e.StoreId], cards: tuple[e.CardShare, ...], store: e.StoreId
           ) -> g.RuleDry | None:
    """The first shown store a card of the mix costs that no card of it makes, when the mix makes `store`."""
    if not any(store in makes(rules, c.card) for c in cards):
        return None
    made = {s for c in cards for s in makes(rules, c.card)}
    short = next((s for c in cards for s in sorted(costs(rules, c.card)) if s in shown and s not in made), None)
    return None if short is None else g.RuleDry(store=str(short), holding=False)
