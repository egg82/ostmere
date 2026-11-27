"""Reading the player's plan: which verbs are dead, which cards orders and the queue would tap, and which mix runs.
Reads only."""
from dataclasses import replace
from enum import Enum

from .answers import AnswerKind, AnswerOffer
from .counts import greyed, is_completed
from .offerstate import is_answered
from .ids import HANDS, CardId, LaneId, MixId
from .index import index
from .lanes import TapCard
from .memo import SaveMemo
from .errors import InvalidVerbError
from .mixes import Mix, MixLayer, SwitchMix, flatten_shares
from .orders import Latch, Order, OrderVerb, listed, rule_on, when_latch
from .rules import Rules
from .state import Save


def is_dead(save: Save, rules: Rules, verb: OrderVerb) -> bool:
    """A switch to a greyed mix, a tap of a completed card, or an answer to an answered offer: a queue entry holding
    one is passed over and kept, but for a tap's and an answer's, which pop at once (schedule.settled_entries). An
    AnswerKind is never dead."""
    if isinstance(verb, AnswerKind):
        return False
    if isinstance(verb, SwitchMix):
        return verb.mix in {m.id for m in save.mixes} and greyed(save, rules, verb.mix)
    if isinstance(verb, AnswerOffer):
        return is_answered(save, rules, verb.offer)
    return verb.card in index(rules).cards and is_completed(save, rules, verb.card)


def is_stuck(save: Save, rules: Rules, verb: OrderVerb) -> bool:
    """A tap whose card nothing will make ready under the current rates (a blocker with no ready time): its entry is kept
    and the ones behind it run (design/cards.txt, "Never ready")."""
    from .work import blocker  # deferred: work -> plan
    if not isinstance(verb, TapCard) or verb.card not in index(rules).cards:
        return False
    b = blocker(save, rules, verb.card)
    return b is not None and b.ready_at is None


def first_live_entry(save: Save, rules: Rules) -> int | None:
    """The index of the first queue entry that is not dead: a stint's mix runs from it, whatever its tap neighbours wait on
    (reading rates, so it never asks whether a tap is stuck)."""
    return next((i for i, e in enumerate(save.queue) if not is_dead(save, rules, e.verb)), None)


def controlling_entry(save: Save, rules: Rules) -> int | None:
    """The index of the entry that controls and whose `until` is watched: the first live one, or, past stuck taps, the first
    live tap that is not stuck (a stint behind a stuck tap waits behind it)."""
    first = first_live_entry(save, rules)
    if first is None:
        return None
    for i in range(first, len(save.queue)):
        verb = save.queue[i].verb
        if is_dead(save, rules, verb) or is_stuck(save, rules, verb):
            continue
        return i if i == first or isinstance(verb, TapCard) else first
    return first


def live_queue_verb(save: Save, rules: Rules) -> OrderVerb | None:
    """The verb of the controlling queue entry."""
    i = controlling_entry(save, rules)
    return None if i is None else save.queue[i].verb


def queue_mix_id(save: Save, rules: Rules) -> MixId | None:
    """The saved hands mix the controlling queue entry switches to, when that entry is a SwitchMix: it runs over the
    player's own until the entry pops, as an order's mix does while latched (design/cards.txt, "Queue mix")."""
    i = first_live_entry(save, rules)
    verb = None if i is None else save.queue[i].verb
    if not isinstance(verb, SwitchMix) or verb.mix not in {m.id for m in save.mixes}:
        return None
    return verb.mix if mix_layer(rules, save.mixes, verb.mix) is MixLayer.HANDS else None


def candidates(save: Save, rules: Rules) -> tuple[CardId, ...]:
    """The known cards a true order or the controlling queue entry would tap, once ready."""
    verbs = [a for _, a, latch in listed(save.orders, save.latches) if rule_on(latch)]
    queued = live_queue_verb(save, rules)
    if queued is not None:
        verbs.append(queued)
    known = index(rules).cards
    return tuple(dict.fromkeys(v.card for v in verbs if isinstance(v, TapCard) and v.card in known))


def mix_layer(rules: Rules, mixes: tuple[Mix, ...], mix: MixId) -> MixLayer:
    """HANDS when every card the mix holds (nested mixes flattened) is on HANDS, TOWN when every card is on a ruled
    lane; a mix holding none is TOWN when a join of the rules makes it or its `layer` says so, else HANDS. InvalidVerbError
    for a mix of both or of a card on neither (design/towns-mix.txt, "THE TOWN'S MIX", "Layer")."""
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
    """The first order that is on and lists a SwitchMix to a saved mix of `layer` that is not greyed, as (its index,
    the first such mix it lists): the order whose mix runs over the player's (engine/design/, "Order mix", "OR ELSE").
    Orders of the other layer never change this layer's running mix."""
    saved = {m.id for m in save.mixes}
    for i, a, latch in listed(save.orders, save.latches):
        if rule_on(latch) and isinstance(a, SwitchMix) and a.mix in saved and not greyed(save, rules, a.mix) \
                and mix_layer(rules, save.mixes, a.mix) is layer:
            return i, a.mix
    return None


def next_placed(save: Save) -> bool:
    """Some rule sits under Next: the row is off the bottom (design/nexts-row.txt, "Next's row")."""
    return any(o.below_next for o in save.orders)


def on_side(save: Save, below: bool) -> Save:
    """`save` with the rules on the other side of Next off (their latches false), for the readers that walk the orders
    in sequence to read one side at a time; `save` itself above a Next at the bottom (design/nexts-row.txt, "Next's row")."""
    if not below and not next_placed(save):
        return save
    return replace(save, latches=tuple(on if o.below_next is below else False for o, on in zip(save.orders, save.latches)))


def under_next(save: Save, rules: Rules) -> Save:
    """on_side(save, below=True), and while the queue has the hands (next_runs) the rules tapping on them off too: they
    wait for the entry (design/nexts-row.txt, "Next's row")."""
    side = on_side(save, below=True)
    if not next_runs(save, rules):
        return side
    cards = index(rules).cards
    hands = tuple(any(isinstance(a, TapCard) and a.card in cards and cards[a.card].lane == HANDS for a in o.actions)
                  for o in save.orders)
    return replace(side, latches=tuple(False if h else on for h, on in zip(hands, side.latches)))


def _hands_rule(save: Save, rules: Rules) -> tuple[int, MixId] | None:
    """The order whose hands mix runs: the first on above Next; else, while the queue runs no mix, the first on under
    Next (design/nexts-row.txt, "Next's row")."""
    above = _mix_rule(on_side(save, below=False), rules, MixLayer.HANDS)
    if above is not None or not next_placed(save) or queue_mix_id(save, rules) is not None:
        return above
    return _mix_rule(on_side(save, below=True), rules, MixLayer.HANDS)


def mix_order(save: Save, rules: Rules) -> int | None:
    """The index of the order whose hands mix runs; None while the queue's or the player's own mix runs."""
    rule = _hands_rule(save, rules)
    return None if rule is None else rule[0]


def next_runs(save: Save, rules: Rules) -> bool:
    """The queue has the hands now: its mix runs (no order's mix above Next runs), or the hands run the controlling
    entry's task."""
    i = controlling_entry(save, rules)
    if i is None:
        return False
    verb = save.queue[i].verb
    if isinstance(verb, TapCard):
        return next(ls.card for ls in save.lanes if ls.lane == HANDS) == verb.card
    return queue_mix_id(save, rules) is not None and _mix_rule(on_side(save, below=False), rules, MixLayer.HANDS) is None


def town_mix_order(save: Save, rules: Rules) -> int | None:
    """The index of the order whose town mix runs; None while nobody runs shares."""
    rule = _mix_rule(save, rules, MixLayer.TOWN)
    return None if rule is None else rule[0]


_RUNNING_MIX: SaveMemo[MixId | None] = SaveMemo(4)
"""A few saves: a handler's save is compared with the one before it (mixpauses.with_running_mix)."""
_RUNNING_TOWN_MIX: SaveMemo[MixId | None] = SaveMemo(4)


def keep_mix_ids(source: Save, target: Save, rules: Rules) -> None:
    """`target` has the discrete state of `source`, all the running mixes' ids read."""
    _RUNNING_MIX.carry(source, target, rules)
    _RUNNING_TOWN_MIX.carry(source, target, rules)


def running_mix_id(save: Save, rules: Rules) -> MixId | None:
    """The mix the hands run now: the mix of mix_order's order, else queue_mix_id, else the player's own (save.active).
    An order under Next runs its mix only while the queue runs none (_hands_rule)."""
    def build() -> MixId | None:
        rule = _hands_rule(save, rules)
        if rule is not None:
            return rule[1]
        queued = queue_mix_id(save, rules)
        return save.active if queued is None else queued
    return _RUNNING_MIX.get(save, rules, build)


def running_town_mix_id(save: Save, rules: Rules) -> MixId | None:
    """The town mix running now: the mix of town_mix_order's order; None when nobody runs shares (the town has no
    mix of the player's own: design/towns-mix.txt, "THE TOWN'S MIX", "Running town mix")."""
    def build() -> MixId | None:
        rule = _mix_rule(save, rules, MixLayer.TOWN)
        return None if rule is None else rule[1]
    return _RUNNING_TOWN_MIX.get(save, rules, build)


def lane_order(save: Save, rules: Rules, lane: LaneId) -> int | None:
    """The index of the first order that is on and lists a tap, not dead, of the card `lane` runs now; None while the
    lane is free or no such order exists (engine/design/, "Lane order"). Presentation only."""
    card = next(ls.card for ls in save.lanes if ls.lane == lane)
    if card is None:
        return None
    return next((i for i, a, latch in listed(save.orders, save.latches)
                 if rule_on(latch) and a == TapCard(card) and not is_dead(save, rules, a)), None)


class OrderState(Enum):
    """Where an order stands now, as evaluation sees it (engine/design/, "Orders", "Order mix")."""

    ON = "on"
    """A mix order whose mix runs (mix_order), or a tap order whose condition holds."""
    WAITING = "waiting"
    """Its condition does not hold (its `when` latch is false)."""
    PAUSED = "paused"
    """Its `when` latch is true and a guard's latch is true (design/rule-guards.txt, "RULE GUARDS")."""
    OUTRANKED = "outranked"
    """A mix order whose condition holds while an earlier mix order's mix runs (mix_order); a tap order whose condition
    holds while its card's lane runs the task of an earlier order (lane_order)."""
    PASSED_OVER = "passed_over"
    """Every action it lists is dead (is_dead): it cannot act whatever its condition."""
    BEHIND_NEXT = "behind_next"
    """A rule under Next that acts on the hands, whose condition holds while the queue has them (next_runs): it would
    otherwise be on, or be outranked by nothing but the queue's mix (design/nexts-row.txt, "Next's row")."""


def order_states(save: Save, rules: Rules) -> tuple[OrderState, ...]:
    """order_states[i]: where save.orders[i] stands now. Presentation only: evaluation reads latches and is_dead."""
    running = {MixLayer.HANDS: mix_order(save, rules), MixLayer.TOWN: town_mix_order(save, rules)}
    cards = index(rules).cards
    lanes = {lane: lane_order(save, rules, lane) for lane in index(rules).lanes}
    queued = next_runs(save, rules)

    def on_hands(o: Order) -> bool:
        verb = o.then
        if isinstance(verb, SwitchMix):
            return _layer_of(save, rules, verb.mix) is MixLayer.HANDS
        return isinstance(verb, TapCard) and verb.card in cards and cards[verb.card].lane == HANDS

    def state(i: int, o: Order, latch: Latch) -> OrderState:
        found = _state(i, o, latch)
        held = found is OrderState.ON or (found is OrderState.OUTRANKED and running[MixLayer.HANDS] is None)
        return OrderState.BEHIND_NEXT if o.below_next and queued and held and on_hands(o) else found

    def _state(i: int, o: Order, latch: Latch) -> OrderState:
        verb = o.then
        if all(is_dead(save, rules, a) for a in o.actions):
            return OrderState.PASSED_OVER
        if not when_latch(latch):
            return OrderState.WAITING
        if not rule_on(latch):
            return OrderState.PAUSED
        if isinstance(verb, SwitchMix):
            return OrderState.ON if running[_layer_of(save, rules, verb.mix)] == i else OrderState.OUTRANKED
        if isinstance(verb, (AnswerOffer, AnswerKind)):
            return OrderState.ON
        lane = next((cards[a.card].lane for a in o.actions if isinstance(a, TapCard) and a.card in cards), None)
        first = None if lane is None else lanes[lane]
        return OrderState.OUTRANKED if first is not None and first < i else OrderState.ON

    return tuple(state(i, o, latch) for i, (o, latch) in enumerate(zip(save.orders, save.latches)))


def order_doing(save: Save, rules: Rules) -> tuple[int | None, ...]:
    """order_doing[i]: the index in save.orders[i].actions of the action it runs now, its lane running that card for
    this rule (lane_order) or the running mix being that mix by this rule; else None. Presentation only."""
    doing: dict[int, OrderVerb] = {}
    for layer in MixLayer:
        rule = _hands_rule(save, rules) if layer is MixLayer.HANDS else _mix_rule(save, rules, layer)
        if rule is not None:
            doing[rule[0]] = SwitchMix(rule[1])
    for ls in save.lanes:
        i = lane_order(save, rules, ls.lane)
        if i is not None and ls.card is not None:
            doing[i] = TapCard(ls.card)
    return tuple(o.actions.index(doing[i]) if i in doing else None for i, o in enumerate(save.orders))
