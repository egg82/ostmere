"""What a Join does to a save: the person is present, and the lane's always task becomes its share in the town mix.
Semantics: DESIGN.txt, "THE TOWN'S MIX", "Join"."""
from dataclasses import replace

from .cards import Join
from .counts import is_retired
from .gates import is_unlocked
from .gone import is_left
from .ids import CardId, LaneId, MixId
from .index import index
from .lanes import TapCard
from .mixes import CardShare, Mix, SwitchMix, flatten_shares
from .orders import AfterTime, Order, initial_latch
from .rules import Rules
from .state import Save
from .unlocks import Unlock, UnlockKind, unlock_key
from .units import BP


def is_joined(save: Save, rules: Rules, lane: LaneId) -> bool:
    return is_unlocked(save, rules, Unlock(UnlockKind.JOINED, lane))


def joined(save: Save, rules: Rules, joins: tuple[Join, ...]) -> Save:
    """Each join in tuple order, unless its lane has joined or left already (then it changes nothing)."""
    for j in joins:
        if not is_joined(save, rules, j.lane) and not is_left(save, j.lane):
            save = _join(save, rules, j)
    return save


def _join(save: Save, rules: Rules, j: Join) -> Save:
    unlocked = set(save.unlocked) | {Unlock(UnlockKind.JOINED, j.lane)}
    save = _with_town_rule(replace(save, unlocked=tuple(sorted(unlocked, key=unlock_key))), j.mix)
    share = _share_card(save, rules, j)
    return _with_share(_without_always_rules(save, rules, j.lane), rules, j, share)


def _with_town_rule(save: Save, mix: MixId) -> Save:
    """The mix, empty, and, unless an equal order is held, the town's always rule at the end of the orders, latched now
    (a rule the player set above it keeps its priority). A mix already saved brings no rule."""
    if any(m.id == mix for m in save.mixes):
        return save
    save = replace(save, mixes=(*save.mixes, Mix(mix, ())))
    rule = Order(AfterTime(0), SwitchMix(mix))
    if rule in save.orders:
        return save
    return replace(save, orders=(*save.orders, rule),
                   latches=(*save.latches, initial_latch(rule.when, None, save.time)))


def _always_rule_card(rules: Rules, lane: LaneId, order: Order) -> CardId | None:
    """The uncapped card an always rule (AfterTime(0), TapCard) on `lane` taps, else None."""
    card = index(rules).cards.get(order.then.card) if isinstance(order.then, TapCard) else None
    if card is None or card.lane != lane or card.cap is not None or order.when != AfterTime(0):
        return None
    return card.id


def _share_card(save: Save, rules: Rules, j: Join) -> CardId | None:
    """The card of the lane's first uncapped always rule that is not retired, else the join's own card."""
    for o in save.orders:
        card = _always_rule_card(rules, j.lane, o)
        if card is not None and not is_retired(save, rules, card):
            return card
    return j.card


def _without_always_rules(save: Save, rules: Rules, lane: LaneId) -> Save:
    """Every always rule on the lane of an uncapped card leaves the orders with its latch; the rest stay."""
    kept = [(o, on) for o, on in zip(save.orders, save.latches) if _always_rule_card(rules, lane, o) is None]
    return replace(save, orders=tuple(o for o, _ in kept), latches=tuple(on for _, on in kept))


def _with_share(save: Save, rules: Rules, j: Join, card: CardId | None) -> Save:
    """The share card at BP in the mix, unless the mix already holds a share of a card on the lane."""
    cards = index(rules).cards
    if card is None or any(cards[s.card].lane == j.lane for s in flatten_shares(save.mixes, j.mix)):
        return save
    return replace(save, mixes=tuple(
        replace(m, components=(*m.components, CardShare(card, BP))) if m.id == j.mix else m for m in save.mixes))
