"""LaneRules (engine DESIGN.txt, "Lane rules"): the count of orders the player set on a ruled lane, read only by a
trigger's when, fired at the decision that sets one."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AtLeast, AtMost, CardCount, CardDef, CardId, ChipDef, ChipId, InvalidRulesError,
    InvalidVerbError, LaneDef, LaneId, LaneRules, LineKey, Order, Outcome, PacingCurve, QueueEntry, Rules, SetOrders,
    SetQueue, SkillDef, SkillId, StoreDef, StoreId, StoreValue, TapCard, TriggerDef, TriggerId, advance_logged, decide,
    decide_logged, new_save, validate_rules,
)
from ashfall_app.engine.discrete import discrete_value

X = StoreId("x")
HELPER, OTHER = LaneId("helper"), LaneId("other")
H, A, B, O = CardId("h"), CardId("a"), CardId("b"), CardId("o")
LINE = LineKey("her_rule")
ALWAYS = AfterTime(0)
RULE = Order(AtMost(StoreValue(X), 5 * Q, 5 * Q), TapCard(A))
COUNT = LaneRules(HELPER)


def world(when: AtLeast | None = None) -> Rules:
    t = TriggerDef(TriggerId("t"), AtLeast(COUNT, 1, 1) if when is None else when, Outcome(lines=(LINE,)))
    r = Rules(stores=(StoreDef(X, 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(HELPER, True), LaneDef(OTHER, True)),
              cards=(CardDef(H, 10), CardDef(A, 10, lane=HELPER), CardDef(B, 25, lane=HELPER),
                     CardDef(O, 10, lane=OTHER)),
              triggers=(t,))
    validate_rules(r)
    return r


def count(orders: tuple[Order, ...]) -> int:
    r = world()
    return discrete_value(replace(new_save(r), orders=orders), r, COUNT)


def test_only_orders_the_player_set_on_the_lane_count():
    assert count(()) == 0
    assert count((Order(ALWAYS, TapCard(A)),)) == 0
    assert count((RULE,)) == 1
    assert count((RULE, Order(AfterTime(7), TapCard(B)))) == 2
    elsewhere = (Order(AtMost(StoreValue(X), 5 * Q, 5 * Q), TapCard(O)), Order(AtLeast(CardCount(H), 1, 1), TapCard(H)))
    assert count(elsewhere) == 0
    assert count((Order(AfterTime(7), TapCard(CardId("unknown"))),)) == 0


def test_the_trigger_fires_at_the_decision_that_sets_the_rule_and_only_once():
    r = world()
    s = new_save(r)
    assert advance_logged(s, r, 1000).lines == ()
    step = decide_logged(s, r, 1000, SetOrders((RULE,)))
    assert [(ln.time, ln.key) for ln in step.lines] == [(1000, LINE)]
    cleared = decide_logged(step.save, r, 2000, SetOrders(()))
    again = decide_logged(cleared.save, r, 3000, SetOrders((RULE,)))
    assert cleared.lines == () and again.lines == ()


def test_an_always_rule_alone_does_not_fire_it():
    r = world()
    assert decide_logged(new_save(r), r, 10, SetOrders((Order(ALWAYS, TapCard(A)),))).lines == ()


@pytest.mark.parametrize("verb", [
    SetOrders((Order(AtLeast(COUNT, 1, 1), TapCard(A)),)),
    SetQueue((QueueEntry(TapCard(H), AtLeast(COUNT, 1, 1)),)),
])
def test_an_order_or_queue_entry_cannot_read_it(verb: SetOrders | SetQueue):
    r = world()
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, verb)


def test_rules_that_misplace_or_misname_it_are_invalid():
    ok = world()
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(ok, chips=(ChipDef(ChipId("c"), AtLeast(COUNT, 1, 1)),)))
    for bad in (LaneRules(LaneId("nowhere")), LaneRules(LaneId("hands"))):
        with pytest.raises(InvalidRulesError):
            validate_rules(world(AtLeast(bad, 1, 1)))
    unruled = replace(ok, lanes=(LaneDef(HELPER, False), LaneDef(OTHER, True)))
    with pytest.raises(InvalidRulesError):
        validate_rules(unruled)
    needing = replace(ok.cards[1], requires=(AtLeast(COUNT, 1, 1),))
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(ok, cards=(ok.cards[0], needing, *ok.cards[2:])))
