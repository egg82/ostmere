"""The LaneRules condition (docs/design/rule-taken-condition.md, "Interface" and "Contract tests (blind)"): the number
of orders in save.orders tapping a card on a ruled lane whose `when` is not AfterTime(0), allowed only as a trigger's
`when`. Docstrings cite the note's numbered contract statements. The count is read through discrete_value and, where
the contract is about the trigger, through the line it lands in decide_logged / advance_logged / rebase_logged."""
from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ashfall_app.engine import (
    AfterTime, AnswerOffer, AtLeast, AtMost, CardDef, ChipDef, ChipId, InvalidRulesError, InvalidVerbError, LaneId, LaneRules,
    LineKey, Order, OrderVerb, Outcome, QueueEntry, RuleInstall, Rules, Save, SetOrders, SetQueue, Step, StoreValue, SwitchMix,
    TapCard, TriggerDef, TriggerId, CardId, Unlock, UnlockKind, Unlocked, advance, advance_logged, decide,
    decide_logged, encode, forecast, new_save, rebase_logged, validate_rules,
)
from ashfall_app.engine.discrete import discrete_value
from cards_world import Q, RACK
from town_world import ASK, H, MIX, R, T1, T2, TC, TOWN, X, YES, always, mixing, started, town

HER = LineKey("her.said")
BIG = AtLeast(StoreValue(X), 90 * Q, 90 * Q)
"""A store rule that stays false in these runs."""
RULE = Order(AtMost(StoreValue(X), 0, 0), TapCard(T1))
"""A rule the player writes on the town lane: x is 0 at the start, so it is true when set."""
HERE = AtLeast(LaneRules(TOWN), 1, 1)


def her_trigger() -> TriggerDef:
    return TriggerDef(TriggerId("her"), HERE, Outcome(lines=(HER,)))


def world() -> Rules:
    """The town world, nothing locked, plus the trigger under test."""
    return town(gated=False, triggers=(her_trigger(),))


def count(s: Save, r: Rules) -> int:
    return discrete_value(s, r, LaneRules(TOWN))


def her(step: Step) -> list[int]:
    """The times at which the step carries the trigger's line."""
    return [ln.time for ln in step.lines if ln.key == HER]


def set_orders(s: Save, r: Rules, t: int, *orders: Order) -> Step:
    return decide_logged(advance(s, r, t), r, t, SetOrders(orders))


# ---- 1 to 3: the count -----------------------------------------------------------------------------------------

def test_1_a_fresh_save_and_an_install_read_zero():
    """Statement 1: LaneRules(L) is 0 in a fresh save, and an install of L's always rule (a trigger's RuleInstall at 10,
    the rule landing in save.orders) leaves it 0; a SetOrders rule then makes it 1 (the control)."""
    r = town(gated=False, triggers=(TriggerDef(TriggerId("inst"), AfterTime(10), Outcome(orders=(RuleInstall(T1),))),))
    s = new_save(r)
    assert count(s, r) == 0
    s = advance(s, r, 50)
    assert s.orders == (always(T1),) and count(s, r) == 0
    assert count(decide(s, r, 50, SetOrders((*s.orders, RULE))), r) == 1


def test_2_a_set_orders_rule_makes_it_one_and_removing_it_makes_it_zero():
    """Statement 2: SetOrders adding AtMost(StoreValue(x)) -> TapCard(t1), t1 on the town lane, reads 1; SetOrders
    removing that order reads 0."""
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((RULE,)))
    assert count(s, r) == 1
    assert count(decide(s, r, 5, SetOrders(())), r) == 0


@pytest.mark.parametrize("order", [
    Order(BIG, TapCard(H)), Order(BIG, TapCard(R)), Order(BIG, SwitchMix(MIX)), always(T1), always(R),
])
def test_3_orders_that_do_not_qualify_are_not_counted(order: Order):
    """Statement 3: a tap on the hands or the rack, a mix order and an AfterTime(0) order on the lane count 0, while the
    qualifying order beside them counts 1 (so the count is reading something)."""
    r = world()
    s = started(r, mixing()[0])
    assert count(decide(s, r, 0, SetOrders((order,))), r) == 0
    assert count(decide(s, r, 0, SetOrders((order, RULE))), r) == 1


def test_3_an_after_time_rule_later_than_zero_counts():
    """Statement 3: an AfterTime(t > 0) order on the lane counts, before it is true."""
    r = world()
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(5), TapCard(T2)),)))
    assert count(s, r) == 1


def test_3_an_order_naming_an_unknown_card_is_not_counted():
    """Statement 3: an order whose card no rules declare counts 0 (the save is built by hand: a verb would refuse it);
    the qualifying order beside it counts 1."""
    r = world()
    bad = Order(BIG, TapCard(CardId("nope")))
    s = replace(new_save(r), orders=(bad,), latches=(False,))
    assert count(s, r) == 0
    s = replace(new_save(r), orders=(bad, RULE), latches=(False, True))
    assert count(s, r) == 1


QUALIFYING = (Order(BIG, TapCard(T1)), RULE, Order(AfterTime(5), TapCard(TC)))
OTHERS = (always(T1), always(R), Order(BIG, TapCard(H)), Order(BIG, TapCard(R)), Order(BIG, SwitchMix(MIX)))


@given(st.lists(st.sampled_from(QUALIFYING + OTHERS), unique=True, max_size=6))
def test_3_the_count_is_the_number_of_qualifying_orders(orders: list[Order]):
    """Statements 2 and 3 as a property: over any set of orders, LaneRules(L) is the number of them tapping a town card
    under a `when` other than AfterTime(0)."""
    r = world()
    s = decide(started(r, mixing()[0]), r, 0, SetOrders(tuple(orders)))
    assert count(s, r) == len([o for o in orders if o in QUALIFYING])


# ---- 4 to 6: when it fires -------------------------------------------------------------------------------------

def test_4_the_trigger_fires_at_the_set_orders_instant_and_only_once():
    """Statement 4: AtLeast(LaneRules(L), 1) fires at the SetOrders instant T, its line in decide_logged's lines at T;
    removing the rule and setting it again never fires it a second time. An order on the rack at T is the control
    that fires nothing."""
    r = world()
    s = advance(new_save(r), r, 20)
    assert her(set_orders(s, r, 20, always(R), Order(BIG, TapCard(H)))) == []
    first = set_orders(s, r, 30, RULE)
    assert her(first) == [30]
    gone = set_orders(first.save, r, 40)
    again = set_orders(gone.save, r, 50, RULE)
    assert her(gone) == [] and her(again) == []
    assert her(advance_logged(again.save, r, 50 + 600)) == []


def test_4_a_rule_set_and_removed_still_landed_the_line():
    """Statement 4 and the lead's answer: a rule the player sets and later removes has still landed the line."""
    r = world()
    step = set_orders(new_save(r), r, 0, RULE)
    assert her(step) == [0] and count(decide(step.save, r, 1, SetOrders(())), r) == 0


def test_5_time_without_decisions_never_fires_it_and_a_forecast_leaves_it_to_a_decision():
    """Statement 5: advancing any length with no decisions fires nothing, even with an always rule installed; a
    forecast neither fires it nor spends it, so the SetOrders that follows still lands the line."""
    r = world()
    s = new_save(r)
    assert her(advance_logged(s, r, 10**6)) == []
    forecast(s, r, 10**6, (X,))
    assert her(set_orders(s, r, 0, RULE)) == [0]


def test_6_changing_the_always_rule_does_not_fire_it():
    """Statement 6: SetOrders editing L's always rule to another card (Change) fires nothing and the count stays 0; a
    rule set after it fires (the control)."""
    r = world()
    s = set_orders(new_save(r), r, 0, always(T1))
    edited = set_orders(s.save, r, 30, always(T2))
    assert her(s) == [] and her(edited) == [] and count(edited.save, r) == 0
    assert her(advance_logged(edited.save, r, 630)) == []
    assert her(set_orders(edited.save, r, 630, always(T2), RULE)) == [630]


def test_6_a_first_install_of_an_always_rule_does_not_fire_it():
    """Statement 6: an answer whose outcome installs an always rule with first=True fires nothing and the count stays
    0 (the control: the rule set by hand afterwards fires)."""
    r = world()
    step = decide_logged(new_save(r), r, 10, AnswerOffer(ASK, YES))
    assert Unlock(UnlockKind.ANSWER, YES) in step.save.unlocked and step.save.orders == (always(TC),)
    assert her(step) == [] and count(step.save, r) == 0
    assert her(set_orders(step.save, r, 20, *step.save.orders, RULE)) == [20]


# ---- 7: where it is refused ------------------------------------------------------------------------------------

def test_7_set_orders_and_set_queue_holding_it_raise_invalid_verb():
    """Statement 7: a SetOrders order's `when` or a SetQueue entry's `until` holding LaneRules raises InvalidVerbError;
    the same verbs on a store condition are accepted."""
    r = world()
    s = new_save(r)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SetOrders((Order(HERE, TapCard(T1)),)))
    verb: OrderVerb = TapCard(H)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SetQueue((QueueEntry(verb, HERE),)))
    decide(s, r, 0, SetOrders((Order(BIG, TapCard(T1)),)))
    decide(s, r, 0, SetQueue((QueueEntry(verb, BIG),)))


def test_7_a_chip_a_card_requires_or_a_trigger_requires_holding_it_is_invalid_rules():
    """Statement 7: rules with LaneRules in a chip's `when`, a card's `requires` or a trigger's `requires` raise
    InvalidRulesError; the same three on a store or unlock condition validate."""
    r = world()
    ok_chip = ChipDef(ChipId("c"), BIG)
    ok_card = CardDef(CardId("rq"), 10, cap=1, requires=(AtLeast(Unlocked(Unlock(UnlockKind.CARD, T1)), 1, 1),))
    ok_trig = TriggerDef(TriggerId("rq"), AfterTime(10), Outcome(), (AtLeast(Unlocked(Unlock(UnlockKind.CARD, T1)), 1, 1),))
    validate_rules(replace(r, chips=(ok_chip,), cards=r.cards + (ok_card,), triggers=r.triggers + (ok_trig,)))
    bad_chip = replace(ok_chip, when=HERE)
    bad_card = replace(ok_card, requires=(HERE,))
    bad_trig = replace(ok_trig, requires=(HERE,))
    for bad in (replace(r, chips=(bad_chip,)), replace(r, cards=r.cards + (bad_card,)),
                replace(r, triggers=r.triggers + (bad_trig,))):
        with pytest.raises(InvalidRulesError):
            validate_rules(bad)


@pytest.mark.parametrize("lane", [RACK, LaneId("nope")])
def test_7_an_unruled_or_unknown_lane_is_invalid_rules(lane: LaneId):
    """Statement 7: LaneRules naming a declared lane that is not ruled, or no lane, raises InvalidRulesError; the
    ruled town lane validates (the control)."""
    bad = TriggerDef(TriggerId("bad"), AtLeast(LaneRules(lane), 1, 1), Outcome())
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(world(), triggers=(bad,)))
    validate_rules(replace(world(), triggers=(replace(bad, when=HERE),)))


# ---- 9: rebase -------------------------------------------------------------------------------------------------

def test_9_a_save_holding_a_qualifying_order_fires_the_new_trigger_at_the_rebase_instant():
    """Statement 9: a save made under rules without the trigger, holding a qualifying order, rebased onto rules that add
    it, lands the line at the rebase instant (500); a save whose rule was removed, and one holding only the always rule,
    land nothing."""
    old = town(gated=False)
    new = replace(old, triggers=old.triggers + (her_trigger(),))
    validate_rules(new)
    held = advance(started(old, SetOrders((RULE,))), old, 500)
    assert her(rebase_logged(encode(held, old), new, ())) == [500]
    removed = advance(decide(held, old, 500, SetOrders(())), old, 600)
    assert her(rebase_logged(encode(removed, old), new, ())) == []
    always_only = advance(started(old, SetOrders((always(T1),))), old, 500)
    assert her(rebase_logged(encode(always_only, old), new, ())) == []


def test_9_the_rebased_save_fires_it_once():
    """Statement 9: after the rebase instant the line is spent; time and a later SetOrders land it no more."""
    old = town(gated=False)
    new = replace(old, triggers=old.triggers + (her_trigger(),))
    held = advance(started(old, SetOrders((RULE,))), old, 500)
    step = rebase_logged(encode(held, old), new, ())
    assert her(step) == [500]
    assert her(advance_logged(step.save, new, 1100)) == []
    assert her(set_orders(step.save, new, 1100, always(T1), RULE)) == []
