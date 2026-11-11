"""Day two's invariants as properties over generated town worlds (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES
AND OFFERS", invariants 57 to 64; town_gen.py). Each save is sampled at its next few events and at offsets, carried
forward (invariant 1). What "can act" means is read off the view: a card on the panel (unlocked, not completed) with
no blocker and a tap time, on a free lane; an offer listed open with that answer."""
from hypothesis import given

from ashfall_app.engine import (
    AfterTime, AnswerOffer, CardId, LaneId, Order, OrderState, OrderVerb, RuleInstall, Rules, Save, SetOrders,
    SwitchMix, TapCard, Unlock, UnlockKind, View, decide, decide_logged, view,
)
from cards_gen import timeline
from cards_world import lane
from town_gen import TOWN_CARDS, TownScenario, play, town_scenario_st
from town_world import unruled


def card_lane(r: Rules, card: CardId) -> LaneId:
    return next(c.lane for c in r.cards if c.id == card)


def tap_can_act(s: Save, r: Rules, v: View, verb: TapCard) -> bool:
    cv = next((c for c in v.cards if c.card == verb.card), None)
    return cv is not None and cv.blocker is None and cv.tap_s is not None and lane(s, card_lane(r, verb.card)).card is None


def answer_can_act(v: View, verb: AnswerOffer) -> bool:
    o = next((o for o in v.offers if o.offer == verb.offer), None)
    return o is not None and o.answer is None and verb.answer in {a.answer for a in o.answers}


def can_act(s: Save, r: Rules, v: View, verb: OrderVerb) -> bool:
    if isinstance(verb, TapCard):
        return tap_can_act(s, r, v, verb)
    if isinstance(verb, AnswerOffer):
        return answer_can_act(v, verb)
    assert isinstance(verb, SwitchMix)   # no AnswerKind in these scenarios
    return verb.mix != s.active


def dead(s: Save, v: View, verb: OrderVerb) -> bool:
    if isinstance(verb, TapCard):
        return verb.card in {c.card for c in v.completed}
    if isinstance(verb, AnswerOffer):
        return Unlock(UnlockKind.ANSWERED, verb.offer) in s.unlocked
    assert isinstance(verb, SwitchMix)   # no AnswerKind in these scenarios
    return verb.mix in v.greyed_mixes


def samples(sc: TownScenario) -> list[tuple[Save, Rules]]:
    r = sc.rules
    return [(x, r) for x in timeline(play(sc)[-1], r, sc.offsets, events=3)]


def cascaded(s: Save) -> bool:
    return s.last_cascade is not None and s.last_cascade.time == s.time


@given(sc=town_scenario_st())
def test_57_every_lane_driven_and_every_answer_given_that_can_be(sc: TownScenario):
    """Invariant 57 with answers: no true order's TapCard or AnswerOffer can act; while no order's mix runs, the
    controlling queue entry's verb cannot act (a switch to the active mix is no change). Instants that hit the cap are
    left out."""
    for s, r in samples(sc):
        if cascaded(s):
            continue
        v = view(s, r)
        for o, on in zip(s.orders, s.latches):
            assert not (on and not isinstance(o.then, SwitchMix) and can_act(s, r, v, o.then)), (s.time, o)
        head = next((e for e in s.queue if not dead(s, v, e.verb)), None)
        if v.mix_order is None and head is not None:
            assert not can_act(s, r, v, head.verb), (s.time, head)


@given(sc=town_scenario_st())
def test_58_orders_drive_a_ruled_lane_as_an_unruled_one(sc: TownScenario):
    """Invariant 58: without the player's own taps of the town (refused when ruled), the same play under the same
    rules with ruled False gives the same saves, step by step and on the timeline after."""
    kept = tuple((dt, v) for dt, v in sc.steps if not (isinstance(v, TapCard) and v.card in TOWN_CARDS))
    sc = TownScenario(sc.rules, kept, sc.offsets)
    a, b = play(sc), play(sc, unruled(sc.rules))
    assert a == b
    assert timeline(a[-1], sc.rules, sc.offsets, 2) == timeline(b[-1], unruled(sc.rules), sc.offsets, 2)


@given(sc=town_scenario_st())
def test_61_an_offer_is_answered_once_by_one_answer(sc: TownScenario):
    """Invariant 61: Unlock(ANSWERED, o) is held exactly when one answer of o is (they enter together), never two."""
    for s, r in [(x, sc.rules) for x in play(sc)] + samples(sc):
        for o in r.offers:
            given = [a.id for a in o.answers if Unlock(UnlockKind.ANSWER, a.id) in s.unlocked]
            assert len(given) == (1 if Unlock(UnlockKind.ANSWERED, o.id) in s.unlocked else 0), (s.time, o.id, given)


def installs_of(r: Rules, before: Save, after: Save) -> set[Order]:
    """The orders the triggers that fired, and the answers given, between `before` and `after` install."""
    found: list[RuleInstall] = []
    for t, was, now in zip(r.triggers, before.fired, after.fired):
        found += list(t.outcome.orders) if now and not was else []
    for o in r.offers:
        for a in o.answers:
            u = Unlock(UnlockKind.ANSWER, a.id)
            found += list(a.outcome.orders) if u in after.unlocked and u not in before.unlocked else []
    return {Order(AfterTime(0), TapCard(i.card)) for i in found}


@given(sc=town_scenario_st())
def test_60_a_cleared_install_comes_back_only_from_a_new_source(sc: TownScenario):
    """Invariant 60: after a SetOrders(()) every order that appears later was installed by a trigger that fired, or an
    answer given, after it (the player sets no ruled always rule in these scenarios, and nothing else after)."""
    r = sc.rules
    end = play(sc)[-1]
    cleared = decide(end, r, end.time, SetOrders(()))
    for s in timeline(cleared, r, sc.offsets, events=4):
        assert set(s.orders) <= installs_of(r, cleared, s), (s.time, s.orders)


@given(sc=town_scenario_st())
def test_63_lane_order_and_outranked(sc: TownScenario):
    """Invariant 63: LaneBar.order is the first i with a true latch, a verb not passed over and a TapCard of the lane's
    running card, else None; a true tap order i not passed over is OUTRANKED exactly when its lane's order is below i."""
    for s, r in samples(sc):
        v = view(s, r)
        orders: dict[LaneId, int | None] = {}
        for b in v.lanes:
            want = next((i for i, o in enumerate(s.orders) if v.orders_on[i] and b.card is not None
                         and v.order_states[i] is not OrderState.PASSED_OVER and o.then == TapCard(b.card)), None)
            assert b.order == want, (s.time, b)
            orders[b.lane] = b.order
        for i, o in enumerate(s.orders):
            if not isinstance(o.then, TapCard) or not v.orders_on[i] or v.order_states[i] is OrderState.PASSED_OVER:
                continue
            at = orders.get(card_lane(r, o.then.card))
            assert (v.order_states[i] is OrderState.OUTRANKED) == (at is not None and at < i), (s.time, i)


@given(sc=town_scenario_st())
def test_64_view_offers_are_the_shown_offers_in_rules_order(sc: TownScenario):
    """Invariant 64: View.offers lists exactly the shown offers (Unlock(OFFER) in View.unlocked), in rules order, with
    `answer` the a whose Unlock(ANSWER, a) is held."""
    for s, r in samples(sc):
        v = view(s, r)
        want = [o for o in r.offers if Unlock(UnlockKind.OFFER, o.id) in v.unlocked]
        assert [o.offer for o in v.offers] == [o.id for o in want]
        for got, o in zip(v.offers, want):
            held = [a.id for a in o.answers if Unlock(UnlockKind.ANSWER, a.id) in s.unlocked]
            assert got.answer == (held[0] if held else None)
            assert [a.answer for a in got.answers] == [a.id for a in o.answers]


@given(sc=town_scenario_st())
def test_62_an_open_offer_answered_by_hand_or_by_order_lands_alike(sc: TownScenario):
    """Invariant 62 on every open offer of the played save, each of its answers: equal stores, cards, lanes, unlocked,
    modifiers and fired; orders differing only by the answer order; equal lines at T."""
    r = sc.rules
    s = play(sc)[-1]
    if cascaded(s):
        return
    for o in view(s, r).offers:
        for a in o.answers if o.answer is None else ():
            verb = AnswerOffer(o.offer, a.answer)
            rule = Order(AfterTime(0), verb)
            x = decide_logged(s, r, s.time, verb)
            y = decide_logged(s, r, s.time, SetOrders(s.orders + (rule,)))
            assert (x.save.stores, x.save.cards, x.save.lanes, x.save.unlocked, x.save.modifiers, x.save.fired) == \
                (y.save.stores, y.save.cards, y.save.lanes, y.save.unlocked, y.save.modifiers, y.save.fired)
            assert [q for q in y.save.orders if q != rule] == list(x.save.orders)
            assert [(ln.key, ln.card) for ln in x.lines if ln.time == s.time] == \
                [(ln.key, ln.card) for ln in y.lines if ln.time == s.time]
