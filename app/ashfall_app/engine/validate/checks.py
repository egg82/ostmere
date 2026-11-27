"""Validation of what the player decides: mixes, conditions, order verbs and modifiers. Raises InvalidVerbError.
"""
from ..offers.answers import AnswerKind, AnswerOffer
from ..cards.counts import is_completed
from ..core.errors import InvalidVerbError
from ..cards.cards import HELD_PREFIX
from ..combat.fightlines import ODDS_PREFIX
from ..unlocks.gates import is_unlocked
from ..core.ids import HANDS, TOWN_PREFIX, LaneId, MixId
from ..core.index import index
from ..people.joins import is_joined
from ..orders.lanes import TapCard
from ..mixes.mixes import MAX_MIXES, CardShare, Mix, MixLayer, SubMix, SwitchMix, flatten_shares
from ..orders.plan import mix_layer
from ..modifiers.modifiers import Modifier, ModifierKind, lowers_cap, lowers_threat
from ..prestige.nodes import NODE_PREFIX
from ..orders.orders import MAX_ACTIONS, MAX_GUARDS, Condition, OrderVerb, Running, Unlocked
from ..core.rules import Rules
from .rules_check import condition_problem, is_lane_rules, subject_problem
from ..core.state import Save
from ..unlocks.unlocks import Unlock, UnlockKind
from ..core.units import BP


def require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidVerbError(message)


def check_mixes(save: Save, rules: Rules, mixes: tuple[Mix, ...]) -> None:
    """Every saved mix, since replacing one can break another that nests it: shares in range and summing to at most
    BP (a town mix's per person), every card known and on HANDS or on a ruled lane, never both. At most MAX_MIXES mixes. The mix being saved
    also holds no locked and no completed card, and in a town mix none capped or on a lane not joined (verbs.SaveMix);
    a new id beginning "town:" is the game's, and a saved mix keeps its layer (design/towns-mix.txt, "THE TOWN'S MIX", "Reserved
    ids")."""
    require(len(mixes) <= MAX_MIXES, f"a save holds at most {MAX_MIXES} mixes")
    old = {m.id for m in save.mixes}
    for mix in mixes:
        require(mix.id in old or not mix.id.startswith(TOWN_PREFIX), f"mix {mix.id}: {TOWN_PREFIX} ids are the game's")
        layer = _check_mix(rules, mixes, mix)
        require(mix.id not in old or layer is mix_layer(rules, save.mixes, mix.id), f"mix {mix.id} keeps its layer")
        if mix not in save.mixes:
            _check_saveable(save, rules, mixes, mix, layer)


def _check_mix(rules: Rules, mixes: tuple[Mix, ...], mix: Mix) -> MixLayer:
    ix = index(rules)
    for c in mix.components:
        require(0 <= c.share_bp <= BP, f"mix {mix.id}: share out of range")
        if isinstance(c, CardShare):
            require(c.card in ix.cards, f"mix {mix.id}: unknown card {c.card}")
            require(ix.cards[c.card].lane == HANDS or ix.cards[c.card].lane in ix.ruled,
                    f"mix {mix.id}: card {c.card} is on a lane no mix runs")
        else:
            require(c.mix in {m.id for m in mixes}, f"mix {mix.id}: unknown mix {c.mix}")
    layer = mix_layer(rules, mixes, mix.id)
    if layer is MixLayer.HANDS:
        require(sum(c.share_bp for c in mix.components) <= BP, f"mix {mix.id}: shares sum past 100%")
    else:
        sums: dict[LaneId, int] = {}
        for s in flatten_shares(mixes, mix.id):
            sums[ix.cards[s.card].lane] = sums.get(ix.cards[s.card].lane, 0) + s.share_bp
        require(all(v <= BP for v in sums.values()), f"mix {mix.id}: one person's shares sum past 100%")
    return layer


def _check_saveable(save: Save, rules: Rules, mixes: tuple[Mix, ...], mix: Mix, layer: MixLayer) -> None:
    cards = index(rules).cards
    for s in flatten_shares(mixes, mix.id):
        require(is_unlocked(save, rules, Unlock(UnlockKind.CARD, s.card)), f"mix {mix.id}: card {s.card} is locked")
        require(not is_completed(save, rules, s.card), f"mix {mix.id}: card {s.card} is completed")
        if layer is MixLayer.TOWN:
            require(cards[s.card].cap is None, f"mix {mix.id}: card {s.card} has a cap")
            lane = cards[s.card].lane
            require(lane in index(rules).pooled or is_joined(save, rules, lane),
                    f"mix {mix.id}: card {s.card}'s person has not joined")


def check_delete(save: Save, mix: MixId) -> None:
    """DeleteMix: the mix is saved, nested in no other saved mix, and named by no order or queue entry."""
    require(mix in {m.id for m in save.mixes}, f"unknown mix {mix}")
    require(not any(isinstance(c, SubMix) and c.mix == mix for m in save.mixes for c in m.components),
            f"mix {mix} is nested in another mix")
    verbs = [a for o in save.orders for a in o.actions] + [e.verb for e in save.queue]
    require(not any(isinstance(v, SwitchMix) and v.mix == mix for v in verbs),
            f"mix {mix} is named by an order or the queue")


def check_condition(rules: Rules, cond: Condition) -> None:
    """Known subject (store, skill, card, unlockable id, runner) and release on the right side of value. LaneRules is
    a trigger's alone: an order or queue entry never holds it."""
    problem = condition_problem(rules, cond)
    require(problem is None, problem or "")
    require(not is_lane_rules(cond), "a lane-rules condition is only a trigger's")


def check_guards(rules: Rules, guards: tuple[Condition, ...]) -> None:
    """An order's guards: at most MAX_GUARDS, none twice, each one SetOrders would accept as a `when` (design/rule-guards.txt,
    "RULE GUARDS")."""
    require(len(guards) <= MAX_GUARDS, f"a rule holds at most {MAX_GUARDS} guards")
    require(len(set(guards)) == len(guards), "a rule holds no guard twice")
    for g in guards:
        check_condition(rules, g)


def check_actions(rules: Rules, mixes: tuple[Mix, ...], actions: tuple[OrderVerb, ...]) -> None:
    """An order's actions, each already a valid order verb: at most MAX_ACTIONS, none twice, and with fallbacks all taps
    of cards on one lane or all mixes of one layer, never an answer (design/or-else.txt, "OR ELSE"). A tap of a card the rules
    do not declare puts no lane in the comparison."""
    require(len(actions) <= MAX_ACTIONS, f"a rule lists at most {MAX_ACTIONS} actions")
    require(len(set(actions)) == len(actions), "a rule lists no action twice")
    if len(actions) == 1:
        return
    require(not isinstance(actions[0], (AnswerOffer, AnswerKind)), "a rule answering an offer has no fallback")
    kind = type(actions[0])
    require(all(type(a) is kind for a in actions), "every action of a rule is the same kind of verb")
    cards = index(rules).cards
    lanes = {cards[a.card].lane for a in actions if isinstance(a, TapCard) and a.card in cards}
    layers = {mix_layer(rules, mixes, a.mix) for a in actions if isinstance(a, SwitchMix)}
    require(len(lanes) <= 1, "every task a rule lists is on one lane")
    require(len(layers) <= 1, "every mix a rule lists is of one layer")


def check_switch(mixes: tuple[Mix, ...], verb: SwitchMix) -> None:
    known: set[MixId] = {m.id for m in mixes}
    require(verb.mix in known, f"unknown mix {verb.mix}")


def check_player_switch(rules: Rules, mixes: tuple[Mix, ...], verb: SwitchMix) -> None:
    """The player's own switch: a saved mix of the hands' layer; a town mix is set by rules."""
    check_switch(mixes, verb)
    require(mix_layer(rules, mixes, verb.mix) is MixLayer.HANDS, f"mix {verb.mix} is set by rules")


def check_modifiers(modifiers: tuple[Modifier, ...]) -> None:
    require(all(m.kind is not ModifierKind.MUL_BP or m.amount_bp >= 0 for m in modifiers), "negative multiplier")
    require(not any(lowers_cap(m) for m in modifiers), "a store cap modifier may only raise the cap")
    require(not any(lowers_threat(m) for m in modifiers), "a threat's strength only rises")
    require(not any(str(m.source).startswith(ODDS_PREFIX) for m in modifiers), "the odds source is the engine's")
    require(not any(str(m.source).startswith(HELD_PREFIX) for m in modifiers), "the held source is the engine's")
    require(not any(str(m.source).startswith(NODE_PREFIX) for m in modifiers), "the node source is a pick's")


def check_discrete(rules: Rules, subject: Unlocked | Running) -> None:
    """The subject names a known unlockable id or runner."""
    problem = subject_problem(rules, subject)
    require(problem is None, problem or "")


def check_hand_tap(rules: Rules, verb: TapCard) -> None:
    """A player's tap: an uncapped card on a ruled lane is set by rules, never tapped by hand; a one-off (a card with a
    cap) is tapped for one completion, as on the hands (design/townsfolk.txt, "Ruled lane")."""
    card = index(rules).cards.get(verb.card)
    require(card is None or card.cap is not None or card.lane not in index(rules).ruled, f"card {verb.card} is set by rules")


def check_queue_verb(rules: Rules, mixes: tuple[Mix, ...], verb: OrderVerb) -> None:
    """A queue entry: the queue is the hands' plan, so it taps no card on a ruled lane (design/townsfolk.txt, "Ruled lane") and
    switches to no town mix, and answers no kind (design/offer-kinds.txt, "OFFER KINDS")."""
    require(not isinstance(verb, AnswerKind), "a queue entry cannot answer a kind: its head is never passed over")
    if isinstance(verb, SwitchMix):
        require(mix_layer(rules, mixes, verb.mix) is MixLayer.HANDS, f"mix {verb.mix} is the town's, not the queue's")
    if isinstance(verb, TapCard):
        card = index(rules).cards.get(verb.card)
        require(card is None or card.lane not in index(rules).ruled, f"card {verb.card} is on a ruled lane")


def check_order_verb(rules: Rules, mixes: tuple[Mix, ...], verb: OrderVerb) -> None:
    """A SwitchMix names a saved mix; an AnswerOffer a declared offer and one of its answers (one not shown yet is
    accepted: planning ahead); a TapCard is checked only when applied (an order may name a card that is locked today
    and unlocked by the time it fires), and never one on a pooled lane (design/groups.txt, "GROUPS (pooled lanes)")."""
    if isinstance(verb, SwitchMix):
        check_switch(mixes, verb)
    if isinstance(verb, TapCard):
        card = index(rules).cards.get(verb.card)
        require(card is None or card.lane not in index(rules).pooled, f"card {verb.card} is on a pooled lane")
    if isinstance(verb, AnswerOffer):
        pair = index(rules).answers.get(verb.answer)
        require(pair is not None and pair[0] == verb.offer, f"answer {verb.answer} is not one of offer {verb.offer}'s")
    if isinstance(verb, AnswerKind):
        require(any(o.kind == verb.kind and any(a.role == verb.role for a in o.answers) for o in rules.offers),
                f"no offer of kind {verb.kind} has the role {verb.role}")
