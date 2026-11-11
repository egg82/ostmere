"""Reading the player's plan: which verbs are dead, which cards orders and the queue would tap, and which mix runs.
Reads only."""
from enum import Enum

from .answers import AnswerKind, AnswerOffer
from .counts import greyed, is_completed
from .offerstate import is_answered
from .ids import CardId, LaneId, MixId
from .index import index
from .lanes import TapCard
from .memo import SaveMemo
from .errors import InvalidVerbError
from .mixes import Mix, MixLayer, SwitchMix, flatten_shares
from .orders import OrderVerb
from .rules import Rules
from .state import Save


def is_dead(save: Save, rules: Rules, verb: OrderVerb) -> bool:
    """A switch to a greyed mix, a tap of a completed card, or an answer to an answered offer: a queue entry holding
    one is passed over and kept (an answer's settles at once: schedule.settled_entries). An AnswerKind is never dead."""
    if isinstance(verb, AnswerKind):
        return False
    if isinstance(verb, SwitchMix):
        return verb.mix in {m.id for m in save.mixes} and greyed(save, rules, verb.mix)
    if isinstance(verb, AnswerOffer):
        return is_answered(save, rules, verb.offer)
    return verb.card in index(rules).cards and is_completed(save, rules, verb.card)


def controlling_entry(save: Save, rules: Rules) -> int | None:
    """The index of the first queue entry that is not dead: the one that controls and whose `until` is watched."""
    return next((i for i, e in enumerate(save.queue) if not is_dead(save, rules, e.verb)), None)


def live_queue_verb(save: Save, rules: Rules) -> OrderVerb | None:
    """The verb of the controlling queue entry."""
    i = controlling_entry(save, rules)
    return None if i is None else save.queue[i].verb


def queue_mix_id(save: Save, rules: Rules) -> MixId | None:
    """The saved hands mix the controlling queue entry switches to, when that entry is a SwitchMix: it runs over the
    player's own until the entry pops, as an order's mix does while latched (DESIGN.txt, "Queue mix")."""
    verb = live_queue_verb(save, rules)
    if not isinstance(verb, SwitchMix) or verb.mix not in {m.id for m in save.mixes}:
        return None
    return verb.mix if mix_layer(rules, save.mixes, verb.mix) is MixLayer.HANDS else None


def candidates(save: Save, rules: Rules) -> tuple[CardId, ...]:
    """The known cards a true order or the controlling queue entry would tap, once ready."""
    verbs = [o.then for o, latch in zip(save.orders, save.latches) if latch]
    queued = live_queue_verb(save, rules)
    if queued is not None:
        verbs.append(queued)
    known = index(rules).cards
    return tuple(dict.fromkeys(v.card for v in verbs if isinstance(v, TapCard) and v.card in known))


def mix_layer(rules: Rules, mixes: tuple[Mix, ...], mix: MixId) -> MixLayer:
    """HANDS when every card the mix holds (nested mixes flattened) is on HANDS, TOWN when every card is on a ruled
    lane; a mix holding none is TOWN when a join of the rules makes it or its `layer` says so, else HANDS. InvalidVerbError
    for a mix of both or of a card on neither (DESIGN.txt, "THE TOWN'S MIX", "Layer")."""
    cards = index(rules).cards
    lanes: set[LaneId] = set()
    for s in flatten_shares(mixes, mix):
        if s.card not in cards:
            raise InvalidVerbError(f"mix {mix}: unknown card {s.card}")
        lanes.add(cards[s.card].lane)
    if not lanes:
        town = mix in index(rules).town_mixes or any(m.id == mix and m.layer is MixLayer.TOWN for m in mixes)
        return MixLayer.TOWN if town else MixLayer.HANDS
    ruled = lanes & index(rules).ruled
    if ruled and lanes != ruled:
        raise InvalidVerbError(f"mix {mix} holds cards of the player's time and of the town's")
    return MixLayer.TOWN if ruled else MixLayer.HANDS


def _layer_of(save: Save, rules: Rules, mix: MixId) -> MixLayer:
    """A saved mix's layer; a mix not saved is the hands' (nothing reads it)."""
    return mix_layer(rules, save.mixes, mix) if mix in {m.id for m in save.mixes} else MixLayer.HANDS


def _mix_rule(save: Save, rules: Rules, layer: MixLayer) -> tuple[int, MixId] | None:
    """The first order whose latch is true and whose verb is a SwitchMix to a saved mix of `layer` that is not greyed,
    as (its index, its mix): the order whose mix runs over the player's (DESIGN.txt, "Order mix"). Orders of the other
    layer never change this layer's running mix."""
    saved = {m.id for m in save.mixes}
    for i, (o, latch) in enumerate(zip(save.orders, save.latches)):
        if latch and isinstance(o.then, SwitchMix) and o.then.mix in saved and not greyed(save, rules, o.then.mix) \
                and mix_layer(rules, save.mixes, o.then.mix) is layer:
            return i, o.then.mix
    return None


def mix_order(save: Save, rules: Rules) -> int | None:
    """The index of the order whose hands mix runs; None while the player's own mix runs."""
    rule = _mix_rule(save, rules, MixLayer.HANDS)
    return None if rule is None else rule[0]


def town_mix_order(save: Save, rules: Rules) -> int | None:
    """The index of the order whose town mix runs; None while nobody runs shares."""
    rule = _mix_rule(save, rules, MixLayer.TOWN)
    return None if rule is None else rule[0]


_RUNNING_MIX: SaveMemo[MixId | None] = SaveMemo(4)
"""A few saves: a handler's save is compared with the one before it (decisions.with_running_mix)."""
_RUNNING_TOWN_MIX: SaveMemo[MixId | None] = SaveMemo(4)


def running_mix_id(save: Save, rules: Rules) -> MixId | None:
    """The mix the hands run now: the mix of mix_order's order, else queue_mix_id, else the player's own (save.active)."""
    def build() -> MixId | None:
        rule = _mix_rule(save, rules, MixLayer.HANDS)
        if rule is not None:
            return rule[1]
        queued = queue_mix_id(save, rules)
        return save.active if queued is None else queued
    return _RUNNING_MIX.get(save, rules, build)


def running_town_mix_id(save: Save, rules: Rules) -> MixId | None:
    """The town mix running now: the mix of town_mix_order's order; None when nobody runs shares (the town has no
    mix of the player's own: DESIGN.txt, "THE TOWN'S MIX", "Running town mix")."""
    def build() -> MixId | None:
        rule = _mix_rule(save, rules, MixLayer.TOWN)
        return None if rule is None else rule[1]
    return _RUNNING_TOWN_MIX.get(save, rules, build)


def lane_order(save: Save, rules: Rules, lane: LaneId) -> int | None:
    """The index of the first order whose latch is true, whose verb is not dead, and whose verb taps the card `lane`
    runs now; None while the lane is free or no such order exists (DESIGN.txt, "Lane order"). Presentation only."""
    card = next(ls.card for ls in save.lanes if ls.lane == lane)
    if card is None:
        return None
    return next((i for i, (o, latch) in enumerate(zip(save.orders, save.latches))
                 if latch and o.then == TapCard(card) and not is_dead(save, rules, o.then)), None)


class OrderState(Enum):
    """Where an order stands now, as evaluation sees it (DESIGN.txt, "Orders", "Order mix")."""

    ON = "on"
    """A mix order whose mix runs (mix_order), or a tap order whose condition holds."""
    WAITING = "waiting"
    """Its condition does not hold (its latch is false)."""
    OUTRANKED = "outranked"
    """A mix order whose condition holds while an earlier mix order's mix runs (mix_order); a tap order whose condition
    holds while its card's lane runs the task of an earlier order (lane_order)."""
    PASSED_OVER = "passed_over"
    """Its verb is dead (is_dead): it cannot act whatever its condition."""


def order_states(save: Save, rules: Rules) -> tuple[OrderState, ...]:
    """order_states[i]: where save.orders[i] stands now. Presentation only: evaluation reads latches and is_dead."""
    running = {MixLayer.HANDS: mix_order(save, rules), MixLayer.TOWN: town_mix_order(save, rules)}
    cards = index(rules).cards
    lanes = {lane: lane_order(save, rules, lane) for lane in index(rules).lanes}

    def state(i: int, verb: OrderVerb, latch: bool) -> OrderState:
        if is_dead(save, rules, verb):
            return OrderState.PASSED_OVER
        if not latch:
            return OrderState.WAITING
        if isinstance(verb, SwitchMix):
            return OrderState.ON if running[_layer_of(save, rules, verb.mix)] == i else OrderState.OUTRANKED
        if isinstance(verb, (AnswerOffer, AnswerKind)):
            return OrderState.ON
        first = lanes[cards[verb.card].lane] if verb.card in cards else None
        return OrderState.OUTRANKED if first is not None and first < i else OrderState.ON

    return tuple(state(i, o.then, latch) for i, (o, latch) in enumerate(zip(save.orders, save.latches)))
