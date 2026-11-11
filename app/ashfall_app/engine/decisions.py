"""Applying verbs: the player's (decide) and those orders and the queue apply.
"""
from dataclasses import replace

from . import plan
from .checks import (
    check_condition, check_delete, check_hand_tap, check_mixes, check_order_verb, check_player_switch, check_queue_verb,
)
from .answering import answered
from .answers import AnswerKind, AnswerOffer
from .conditions import subject_value
from .errors import InvalidVerbError
from .cards import LaneState
from .counts import completions, unit, work_value
from .cure_reading import cures_shown
from .ids import HANDS, CardId, LaneId, LineKey
from .index import index
from .installs import requeued
from .lanes import TapCard
from .mixes import Mix, MixLayer, SwitchMix
from .offerstate import acting, refusal
from .orders import AfterTime, Condition, Order, OrderVerb, initial_latch
from .prestige import applied
from .prestigeverbs import MovePick, Prestige, UndoPick, refuse_by_hand
from .rates import lane_state
from .rebuild import rebuild
from .rules import Rules
from .state import Save
from .verbs import DeleteMix, SaveMix, SetOrders, SetQueue, Verb
from .work import blocker, interrupt, ready, tap, tap_seconds

type PlanVerb = SwitchMix | SaveMix | DeleteMix | SetOrders | SetQueue | TapCard
"""Every verb but the answers and the prestige verbs, which apply_verb handles first."""


def switch(save: Save, rules: Rules, verb: SwitchMix) -> Save:
    """Make a saved mix the player's own (save.active). Switching to the active mix changes nothing. A greyed mix may
    be made active by the player (nothing in it runs). While an order's mix runs, this sets only the mix that comes
    back (DESIGN.txt, "Order mix")."""
    if verb.mix == save.active:
        return save
    return with_running_mix(save, rules, replace(save, active=verb.mix))


def with_running_mix(before: Save, rules: Rules, after: Save) -> Save:
    """`after`, with every pause cleared and rates rebuilt if its running mix is not `before`'s, else as given."""
    if (plan.running_mix_id(after, rules), plan.running_town_mix_id(after, rules)) == (
            plan.running_mix_id(before, rules), plan.running_town_mix_id(before, rules)):
        return after
    return rebuild(replace(after, pauses=()), rules)


def apply_order_verb(save: Save, rules: Rules, verb: OrderVerb) -> tuple[Save, tuple[LineKey, ...]]:
    """What an order or the queue head does, and the lines it emits: a TapCard taps as an order would; an AnswerOffer
    that can act answers, and one that cannot changes nothing; an AnswerKind answers the offer it resolves to. A
    SwitchMix changes nothing here: an order's mix runs while it is latched, the queue's while its entry controls
    (plan.running_mix_id)."""
    if isinstance(verb, TapCard):
        return tap(save, rules, verb, by_player=False), ()
    if isinstance(verb, (AnswerOffer, AnswerKind)):
        found = acting(save, rules, verb)
        return (save, ()) if found is None else answered(save, rules, found)
    return save, ()


def controlling_verb(save: Save, rules: Rules) -> OrderVerb | None:
    """The verb evaluation applies next, from the first of its sources that has one: the answer orders, the tap orders,
    then the queue (DESIGN.txt, "Orders", "Order mix"; TOWNSFOLK, INSTALLED RULES AND OFFERS, "Evaluation applies
    every verb")."""
    for source in (_answer_order_verb, _tap_order_verb, _queue_verb):
        verb = source(save, rules)
        if verb is not None:
            return verb
    return None


def _answer_order_verb(save: Save, rules: Rules) -> AnswerOffer | None:
    """The AnswerOffer of the first order whose latch is true and whose answer can act (an AnswerKind as the offer it
    resolves to); the rest are skipped."""
    for order, latch in zip(save.orders, save.latches):
        if latch and isinstance(order.then, (AnswerOffer, AnswerKind)) and (found := acting(save, rules, order.then)):
            return found
    return None


def _tap_order_verb(save: Save, rules: Rules) -> TapCard | None:
    """The TapCard of the first order whose latch is true and whose card can act (ready, and its speed above 0);
    orders that cannot act are skipped, never chosen."""
    for order, latch in zip(save.orders, save.latches):
        if latch and isinstance(order.then, TapCard) and _can_act(save, rules, order.then):
            return order.then
    return None


def _can_act(save: Save, rules: Rules, verb: TapCard) -> bool:
    """A tap of verb.card now by an order or the queue would start it: ready and its speed above 0 (tap_seconds not
    None)."""
    return ready(save, rules, verb.card) and tap_seconds(save, rules, verb.card) is not None


def _queue_verb(save: Save, rules: Rules) -> OrderVerb | None:
    """The verb of the controlling queue entry (the first not dead: a switch to a greyed mix, a tap of a completed
    card), which waits rather than being passed over for being unready; while an order's mix runs, only when it takes
    up a hands task with kept work (_resumes)."""
    verb = plan.live_queue_verb(save, rules)
    return verb if plan.mix_order(save, rules) is None or _resumes(save, rules, verb) else None


def _resumes(save: Save, rules: Rules, verb: OrderVerb | None) -> bool:
    """`verb` taps a HANDS card stopped mid-completion (a cure cut in on it, or a dry store stopped it). As a tap it held
    the hands over any order's mix, so it takes them back over one (DESIGN.txt, "CURE CUT-IN")."""
    if not isinstance(verb, TapCard):
        return False
    c = index(rules).cards.get(verb.card)
    return c is not None and c.lane == HANDS and work_value(save, verb.card) % unit(c) != 0


def holds(save: Save, rules: Rules, lane: LaneId, card: CardId) -> bool:
    """The lane's task holds: were the lane free now, evaluation's controlling verb would tap `card` again."""
    return controlling_verb(_freed(save, lane), rules) == TapCard(card)


def cuts_in(save: Save, rules: Rules, card: CardId) -> bool:
    """A player's tap of `card` now takes the hands from the task they run: a glowing step (_glow_cuts_in) or a cure
    (cure_cuts_in)."""
    return _glow_cuts_in(save, rules, card) or cure_cuts_in(save, rules, card)


def _glow_cuts_in(save: Save, rules: Rules, card: CardId) -> bool:
    """`card` glows, is on the hands, has never completed and would start were they free, and the task is one the queue
    or an order would start again once `card` lands (holds), or one an order names (_ordered), so the cut-in loses
    nothing (DESIGN.txt, "Cut-in")."""
    c = index(rules).cards.get(card)
    if c is None or not c.glows or c.lane != HANDS:
        return False
    running = lane_state(save, HANDS).card
    if running is None or running == card:
        return False
    return completions(save, rules, card) == 0 and _can_act(_freed(save, HANDS), rules, TapCard(card)) \
        and (holds(save, rules, HANDS, running) or _ordered(save, running))


def _ordered(save: Save, card: CardId) -> bool:
    """An order taps `card`, true or not: a stage that drinks the store its own order watches has dropped that order's
    latch by the middle of the stage, which does not make the stage a hand tap (DESIGN.txt, "ORDER CARD ON A STAGED
    BUILD")."""
    return any(o.then == TapCard(card) for o in save.orders)


def cure_cuts_in(save: Save, rules: Rules, card: CardId) -> bool:
    """A player's tap of `card` now takes the hands from the task they run: `card` is on the hands
    and a cure for a chip shown now, the task is not one, and `card` would start were the hands free (DESIGN.txt,
    "CURE CUT-IN")."""
    c = index(rules).cards.get(card)
    if c is None or c.lane != HANDS:
        return False
    running = lane_state(save, HANDS).card
    if running is None or running == card:
        return False
    return cures_shown(save, rules, card) and not cures_shown(save, rules, running) \
        and _can_act(_freed(save, HANDS), rules, TapCard(card))


def cut_in(save: Save, rules: Rules) -> Save:
    """The hands' task interrupted where it stands, its work kept; a task no true order or queue entry taps goes to the
    queue's front as the page's When ready entry for its current completion (installs.queued), so it is taken up
    again (DESIGN.txt, "CURE CUT-IN")."""
    running = lane_state(save, HANDS).card
    assert running is not None, "a cut-in needs a task on the hands"
    return requeued(interrupt(save, rules, HANDS), rules, running)


def _freed(save: Save, lane: LaneId) -> Save:
    return replace(save, lanes=tuple(LaneState(ls.lane) if ls.lane == lane else ls for ls in save.lanes))


def candidates(save: Save, rules: Rules) -> tuple[CardId, ...]:
    """The cards a true order or the controlling queue entry would tap, once ready."""
    return plan.candidates(save, rules)


def apply_verb(save: Save, rules: Rules, verb: Verb) -> tuple[Save, bool, tuple[LineKey, ...]]:
    """The save after the player's verb, whether orders and the queue must evaluate now (SetOrders, SetQueue, and
    DeleteMix of the active mix), and the lines it emits. A prestige verb is prestige.applied's."""
    if isinstance(verb, (Prestige, UndoPick, MovePick)):
        return applied(save, rules, verb), True, ()
    if isinstance(verb, AnswerKind):
        raise InvalidVerbError("the player answers an offer, not a kind")
    if isinstance(verb, AnswerOffer):
        problem = refusal(save, rules, verb)
        if problem is not None:
            raise InvalidVerbError(problem)
        after, lines = answered(save, rules, verb)
        return after, True, lines
    save, must_evaluate = _applied(save, rules, verb)
    return save, must_evaluate, ()


def _applied(save: Save, rules: Rules, verb: PlanVerb) -> tuple[Save, bool]:
    if isinstance(verb, SwitchMix):
        check_player_switch(rules, save.mixes, verb)
        return switch(save, rules, verb), False
    if isinstance(verb, SaveMix):
        return _save_mix(save, rules, verb.mix), False
    if isinstance(verb, TapCard):
        check_hand_tap(rules, verb)
        if cuts_in(save, rules, verb.card):
            save = cut_in(save, rules)
        return tap(save, rules, verb, by_player=True), False
    if isinstance(verb, DeleteMix):
        return _delete_mix(save, rules, verb)
    if isinstance(verb, SetOrders):
        for o in verb.orders:
            refuse_by_hand(o.then)
            check_condition(rules, o.when)
            check_order_verb(rules, save.mixes, o.then)
        latches = tuple(_kept_latch(save, rules, o) for o in verb.orders)
        return with_running_mix(save, rules, replace(save, orders=verb.orders, latches=latches)), True
    for e in verb.entries:
        refuse_by_hand(e.verb)
        check_condition(rules, e.until)
        check_order_verb(rules, save.mixes, e.verb)
        check_queue_verb(rules, save.mixes, e.verb)
    return with_running_mix(save, rules, replace(save, queue=verb.entries)), True


def failed_tap(save: Save, rules: Rules, verb: Verb) -> CardId | None:
    """The card when `verb` is a player's TapCard that apply_verb accepted on `save` and its card is unready there: a
    failed tap, which changed nothing (DESIGN.txt, "Failed tap"); else None."""
    return verb.card if isinstance(verb, TapCard) and blocker(save, rules, verb.card) is not None else None


def _kept_latch(save: Save, rules: Rules, order: Order) -> bool:
    """The latch of the first order in save.orders equal to `order`, matched as rulelog.py matches them, so a kept or
    moved rule holds its place in its band; else latch_now, for a new or edited one (DESIGN.txt, "Rule changes")."""
    for old, on in zip(save.orders, save.latches):
        if old == order:
            return on
    return latch_now(save, rules, order.when)


def latch_now(save: Save, rules: Rules, cond: Condition) -> bool:
    """The latch a condition starts with at save.time (orders.initial_latch on its subject's value now)."""
    value = None if isinstance(cond, AfterTime) else subject_value(save, rules, cond.subject)
    return initial_latch(cond, value, save.time)


def _save_mix(save: Save, rules: Rules, mix: Mix) -> Save:
    ids = [m.id for m in save.mixes]
    was = next((plan.mix_layer(rules, save.mixes, m.id) for m in save.mixes if m.id == mix.id), MixLayer.HANDS)
    mix = replace(mix, layer=was if not mix.components else MixLayer.HANDS)
    mixes = tuple(mix if m.id == mix.id else m for m in save.mixes) if mix.id in ids else save.mixes + (mix,)
    check_mixes(save, rules, mixes)
    saved = replace(save, mixes=mixes)
    if mix.id not in (plan.running_mix_id(saved, rules), plan.running_town_mix_id(saved, rules)):
        return with_running_mix(save, rules, saved)
    return rebuild(replace(saved, pauses=()), rules)


def _delete_mix(save: Save, rules: Rules, verb: DeleteMix) -> tuple[Save, bool]:
    check_delete(save, verb.mix)
    kept = replace(save, mixes=tuple(m for m in save.mixes if m.id != verb.mix))
    if verb.mix != save.active:
        return kept, False
    return with_running_mix(save, rules, replace(kept, active=None)), True
