"""What a Join does to a save: the person is present, and the lane's always task becomes its share in the town mix.
Semantics: design/towns-mix.txt, "THE TOWN'S MIX", "Join"."""
from dataclasses import replace

from ..cards.cards import Join
from ..cards.counts import is_retired
from ..unlocks.gates import is_unlocked
from .gone import is_left
from ..core.ids import CardId, LaneId, MixId
from ..core.index import index
from ..orders.lanes import TapCard
from ..mixes.mixes import CardShare, Mix, SwitchMix, flatten_shares
from ..orders.installs import without_actions
from ..orders.orders import AfterTime, Order, OrderVerb, initial_latch, placed, unplaced
from ..core.rules import Rules
from ..core.state import Save
from ..unlocks.unlocks import Unlock, UnlockKind, unlock_key
from ..core.units import BP


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
    if j.own_split:
        return with_share(_without_always_rules(save, rules, j.lane), rules, j.lane, j.mix, _share_card(save, rules, j))
    save = replace(save, lanes=tuple(replace(ls, own_split=False) if ls.lane == j.lane else ls for ls in save.lanes))
    return with_share(_without_always_rules(save, rules, j.lane), rules, _group(rules, j.lane), j.mix, j.card)


def _with_town_rule(save: Save, mix: MixId) -> Save:
    """The mix, empty, and, unless an equal order is held, the town's always rule at the end of the orders, latched now
    (a rule the player set above it keeps its priority). A mix already saved brings no rule."""
    if any(m.id == mix for m in save.mixes):
        return save
    save = replace(save, mixes=(*save.mixes, Mix(mix, ())))
    rule = Order(AfterTime(0), SwitchMix(mix))
    if rule in map(unplaced, save.orders):
        return save
    return replace(save, orders=placed((*save.orders, rule)),
                   latches=(*save.latches, initial_latch(rule.when, None, save.time)))


def _always_rule_card(rules: Rules, lane: LaneId, order: Order, verb: OrderVerb) -> CardId | None:
    """The uncapped card `verb`, one of an always rule's (AfterTime(0)) actions, taps on `lane`, else None."""
    card = index(rules).cards.get(verb.card) if isinstance(verb, TapCard) else None
    if card is None or card.lane != lane or card.cap is not None or order.when != AfterTime(0):
        return None
    return card.id


def _share_card(save: Save, rules: Rules, j: Join) -> CardId | None:
    """The card of the lane's first uncapped always rule that is not retired, else the join's own card."""
    for o in save.orders:
        for a in o.actions:
            card = _always_rule_card(rules, j.lane, o, a)
            if card is not None and not is_retired(save, rules, card):
                return card
    return j.card


def _without_always_rules(save: Save, rules: Rules, lane: LaneId) -> Save:
    """Every always rule's tap of an uncapped card on the lane leaves the orders (without_actions); the rest stay."""
    return without_actions(save, lambda o, a: _always_rule_card(rules, lane, o, a) is not None)


def _group(rules: Rules, lane: LaneId) -> LaneId | None:
    return next((d.group for d in rules.lanes if d.id == lane), None)


def with_share(save: Save, rules: Rules, lane: LaneId | None, mix: MixId, card: CardId | None) -> Save:
    """The share card at BP in the mix, unless the mix already holds a share of a card on `lane` (a person's lane, or
    the group an unmarked person's share goes to)."""
    cards = index(rules).cards
    if card is None or any(cards[s.card].lane == lane for s in flatten_shares(save.mixes, mix)):
        return save
    return replace(save, mixes=tuple(
        replace(m, components=(*m.components, CardShare(card, BP))) if m.id == mix else m for m in save.mixes))
