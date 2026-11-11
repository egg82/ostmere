"""The town's mix (engine DESIGN.txt, "THE TOWN'S MIX"): unit tests written beside the implementation, to develop it.
The contract tests of invariants 90 to 97 are written blind elsewhere."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, AfterTime, AtLeast, CardCount, CardDef, CardId, CardShare, Flow, InvalidRulesError,
    InvalidVerbError, Join, LaneDef, LaneId, Mix, MixId, Order, OrderState, Outcome, PacingCurve, QueueEntry, Rules, Save, SaveMix,
    SetOrders, SetQueue, SkillDef, SkillId, StoreDef, StoreId, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind,
    advance, decide, new_save, validate_rules, view,
)
from ashfall_app.engine.mixes import MixLayer
from ashfall_app.engine.modifiers import RunKind
from ashfall_app.engine.plan import mix_layer

X = StoreId("x")
P1, P2, P3 = LaneId("p1"), LaneId("p2"), LaneId("p3")
H, A1, B1, C1, A2 = CardId("h"), CardId("a1"), CardId("b1"), CardId("c1"), CardId("a2")
TOWN = MixId("town:main")
ALWAYS = AfterTime(0)
JOIN = TriggerId("join")


def world(*, joins: tuple[Join, ...] = (), at: int = 1000, extra: tuple[CardDef, ...] = ()) -> Rules:
    """Two people (p1 with a1, b1 uncapped and c1 capped, p2 with a2) and a lane p3 that never joins."""
    cards = (CardDef(H, 100, makes=(Flow(X, Q),)), CardDef(A1, 100, makes=(Flow(X, Q),)), CardDef(B1, 50),
             CardDef(C1, 50, cap=2), CardDef(A2, 100, makes=(Flow(X, 2 * Q),)), *extra)
    cards = tuple(replace(c, lane=P2) if c.id == A2 else replace(c, lane=P1) if c.id in (A1, B1, C1) else c
                  for c in cards)
    triggers = (TriggerDef(JOIN, AfterTime(at), Outcome(joins=joins)),) if joins else ()
    r = Rules(stores=(StoreDef(X, 10**6 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(P1, True), LaneDef(P2, True), LaneDef(P3, True)),
              cards=cards, triggers=triggers)
    validate_rules(r)
    return r


def x_at(r: Rules, s: Save, t: int) -> int:
    return next(st.segment.start_value for st in advance(s, r, t).stores if st.store == X)


def test_a_join_makes_the_always_task_a_share_and_keeps_what_the_lane_makes():
    r = world(joins=(Join(P1, TOWN),))
    plain = world()
    orders = SetOrders((Order(ALWAYS, TapCard(A1)),))
    s = decide(new_save(r), r, 0, orders)
    base = decide(new_save(plain), plain, 0, orders)
    after = advance(s, r, 1001)
    assert Unlock(UnlockKind.JOINED, P1) in after.unlocked
    assert after.orders == (Order(ALWAYS, SwitchMix(TOWN)),) and after.latches == (True,)
    assert after.mixes == (Mix(TOWN, (CardShare(A1, BP),)),)
    for t in (1001, 1050, 1100, 1234, 5000):
        assert advance(s, r, t).stores == advance(base, plain, t).stores
        assert advance(s, r, t).cards == advance(base, plain, t).cards
    v = view(after, r)
    assert v.running_town_mix == TOWN and v.town_mix_order == 0 and v.running_mix is None and v.mix_order is None


def test_a_non_always_rule_on_the_lane_stays_and_yields_the_shares_while_it_taps():
    r = world(joins=(Join(P1, TOWN),))
    rule = Order(AtLeast(CardCount(A1), 15, 15), TapCard(B1))
    s = decide(new_save(r), r, 0, SetOrders((rule, Order(ALWAYS, TapCard(A1)))))
    before = advance(s, r, 1200)
    assert rule in before.orders and Order(ALWAYS, TapCard(A1)) not in before.orders
    assert before.lanes[1].card is None
    a1 = next(c for c in view(before, r).cards if c.card == A1)
    assert (a1.share_bp, a1.run) == (BP, RunKind.FULL)
    later = advance(s, r, 2000)   # a1 has 15 completions by now; the rule holds the person with b1 for good
    assert later.lanes[1].card == B1
    a1 = next(c for c in view(later, r).cards if c.card == A1)
    assert (a1.share_bp, a1.run, a1.by) == (BP, RunKind.YIELDED, None)
    assert x_at(r, later, 2500) == x_at(r, later, 2000) and x_at(r, before, 1300) > x_at(r, before, 1200)


def test_a_second_person_joins_the_same_mix_and_keeps_its_own_time():
    r = world(joins=(Join(P1, TOWN), Join(P2, TOWN, A2)))
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1)),)))
    s = advance(s, r, 1001)
    (mix,) = s.mixes
    assert mix.components == (CardShare(A1, BP), CardShare(A2, BP))
    assert len([o for o in s.orders if o == Order(ALWAYS, SwitchMix(TOWN))]) == 1
    assert Unlock(UnlockKind.JOINED, P2) in s.unlocked
    solo = world(joins=(Join(P1, TOWN),))
    t = decide(new_save(solo), solo, 0, SetOrders((Order(ALWAYS, TapCard(A1)),)))
    grown = x_at(r, s, 1101) - x_at(r, s, 1001)
    assert grown > 0 and grown == 3 * (x_at(solo, t, 1101) - x_at(solo, t, 1001))   # a1 makes 1, a2 makes 2, unshared


def test_the_tests_see_x_move():
    """A control: the stores these tests compare are moving, not stuck at a cap."""
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1)),)))
    assert 0 < x_at(r, s, 500) < x_at(r, s, 900)


def test_a_town_mix_is_saved_only_for_joined_uncapped_cards_within_each_persons_time():
    r = world(joins=(Join(P1, TOWN),))
    s = advance(decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1)),))), r, 1001)
    ok = Mix(TOWN, (CardShare(A1, 6000), CardShare(B1, 4000)))
    decide(s, r, 1001, SaveMix(ok))
    bad = [Mix(TOWN, (CardShare(A1, 6000), CardShare(B1, 4001))),          # one person past 100%
           Mix(TOWN, (CardShare(A1, 5000), CardShare(A2, 5000))),          # a person who has not joined
           Mix(TOWN, (CardShare(A1, 5000), CardShare(C1, 5000))),          # a capped card
           Mix(TOWN, (CardShare(A1, 5000), CardShare(H, 5000))),           # both layers
           Mix(MixId("town:new"), (CardShare(A1, 5000),)),                  # an id only a join creates
           Mix(MixId("mine"), (CardShare(A1, 5000), CardShare(A2, 5000)))]
    for mix in bad:
        with pytest.raises(InvalidVerbError):
            decide(s, r, 1001, SaveMix(mix))
    both = world(joins=(Join(P1, TOWN), Join(P2, TOWN, A2)))
    s2 = advance(decide(new_save(both), both, 0, SetOrders((Order(ALWAYS, TapCard(A1)),))), both, 1001)
    decide(s2, both, 1001, SaveMix(Mix(TOWN, (CardShare(A1, BP), CardShare(A2, BP)))))   # two people, each whole


def test_a_town_mix_is_the_towns_never_the_players_or_the_queues():
    r = world(joins=(Join(P1, TOWN),))
    s = advance(decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1)),))), r, 1001)
    with pytest.raises(InvalidVerbError, match="set by rules"):
        decide(s, r, 1001, SwitchMix(TOWN))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 1001, SetQueue((QueueEntry(SwitchMix(TOWN), AtLeast(CardCount(H), 1, 1)),)))
    assert mix_layer(r, s.mixes, TOWN) is MixLayer.TOWN
    assert s.active is None


def test_hands_and_town_orders_each_run_their_own_layer():
    r = world(joins=(Join(P1, TOWN),))
    s = advance(decide(new_save(r), r, 0, SetOrders((Order(ALWAYS, TapCard(A1)),))), r, 1001)
    s = decide(s, r, 1001, SaveMix(Mix(MixId("hm"), (CardShare(H, BP),))))
    s = decide(s, r, 1001, SetOrders((Order(ALWAYS, SwitchMix(MixId("hm"))), *s.orders)))
    v = view(s, r)
    assert (v.running_mix, v.mix_order) == ("hm", 0) and (v.running_town_mix, v.town_mix_order) == (TOWN, 1)
    assert v.order_states[:2] == (OrderState.ON, OrderState.ON)
    s = decide(s, r, 1001, SetOrders((Order(ALWAYS, SwitchMix(MixId("hm"))),)))
    assert view(s, r).running_town_mix is None and view(s, r).running_mix == "hm"


def test_validation_refuses_a_misplaced_join_and_xp_on_a_ruled_lane_card():
    outcome_joins = (Join(P1, TOWN),)
    base = world(joins=outcome_joins)
    for bad in (Join(HANDS, TOWN), Join(LaneId("nope"), TOWN), Join(P1, MixId("mine")), Join(P1, TOWN, C1), Join(P1, TOWN, A2)):
        with pytest.raises(InvalidRulesError):
            validate_rules(replace(base, triggers=(TriggerDef(JOIN, AfterTime(1), Outcome(joins=(bad,))),)))
    on_card = replace(base.cards[1], outcome=Outcome(joins=outcome_joins))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(base, cards=(base.cards[0], on_card, *base.cards[2:])))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(base, cards=(*base.cards, CardDef(CardId("xp"), 10, lane=P3, skill=SkillId("k"), xp_per_hour=Q))))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(base, opening=(Unlock(UnlockKind.JOINED, P1),)))
