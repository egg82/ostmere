"""Step.rule_changes (engine/rulelog.py): each order's latch turning true (it comes on) or false (it lets go) on the way
to a logged step, with the time and the amount of the store its condition reads. Orders have no id, so an order is
matched across a change by what it says: a reorder reports nothing, an edit reports the edited order as new. Recording
changes nothing: the logged save is the plain one."""
from ashfall_app.engine import (
    BP, AfterTime, AtMost, CardShare, Flow, Mix, Order, SaveMix, SetOrders, StoreDef, StoreValue, SwitchMix,
    advance, advance_logged, decide, decide_logged, new_save, value,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, store_id

S0 = store_id(0)
M0, M1 = mix_id(0), mix_id(1)
LOW = Order(AtMost(StoreValue(S0), 3 * Q, 8 * Q), SwitchMix(M0))
"""On at 3 or under, let go past 8: m0 refills s0 at 2/h, the player's m1 drains it at 1/h."""
NEVER = Order(AfterTime(10**9), SwitchMix(M1))


def _world():
    """s0 at 5 of 10; m0 = {c0, making 2/h}, m1 = {c1, using 1/h}, m1 the player's; LOW set at 0."""
    rules = make_rules([StoreDef(S0, 10 * Q, 5 * Q)], [card(0, 0, (Flow(S0, 2000),), ()), card(1, 0, (), (Flow(S0, 1000),))])
    s = new_save(rules)
    for v in (SaveMix(Mix(M0, (CardShare(card_id(0), BP),))), SaveMix(Mix(M1, (CardShare(card_id(1), BP),))),
              SwitchMix(M1), SetOrders((LOW,))):
        s = decide(s, rules, 0, v)
    return rules, s


def test_a_cycling_rule_reports_each_start_and_let_go_with_the_store_level():
    rules, s = _world()
    changes = advance_logged(s, rules, 20 * 3600).rule_changes
    assert len(changes) >= 4   # control: it cycles inside the span
    assert [c.on for c in changes] == [i % 2 == 0 for i in range(len(changes))]
    assert all(c.order == LOW for c in changes)
    assert changes[0].time == 2 * 3600 and changes[0].level == 3 * Q   # 5 drained at 1/h reaches 3 at 2h
    for c in changes:
        assert c.level is not None and (c.level <= 3 * Q if c.on else c.level > 8 * Q)
    assert [c.time for c in changes] == sorted(c.time for c in changes)


def test_recording_changes_nothing():
    rules, s = _world()
    assert advance_logged(s, rules, 20 * 3600).save == advance(s, rules, 20 * 3600)


def test_a_reorder_reports_nothing_and_an_edit_reports_the_edited_rule_as_new():
    rules, s = _world()
    on = advance(s, rules, 2 * 3600)   # at 3 exactly, so even latched afresh the edit below holds
    assert on.latches == (True,)   # control: LOW is on
    assert decide_logged(on, rules, on.time, SetOrders((NEVER, LOW))).rule_changes == ()
    edited = Order(AtMost(StoreValue(S0), 3 * Q, 9 * Q), SwitchMix(M0))
    changes = decide_logged(on, rules, on.time, SetOrders((edited,))).rule_changes
    assert [(c.order, c.on) for c in changes] == [(edited, True)]


def _mid_band():
    """LOW on with s0 at 7, between its when (3) and its until (8): on at 2h, then m0 alone refills it at 2/h."""
    rules, s = _world()
    s = advance(s, rules, 4 * 3600)
    assert s.latches == (True,) and value(s, rules, S0, s.time) == 7 * Q   # control: running, and mid-band
    return rules, s


def test_a_rule_running_mid_band_stays_on_when_another_rule_is_added_or_edited():
    rules, s = _mid_band()
    s = decide(s, rules, s.time, SetOrders((LOW, NEVER)))
    assert s.latches == (True, False)
    edited = Order(AfterTime(2 * 10**9), SwitchMix(M1))
    step = decide_logged(s, rules, s.time, SetOrders((LOW, edited)))
    assert step.save.latches == (True, False) and step.rule_changes == ()


def test_a_rule_running_mid_band_stays_on_through_a_reorder():
    rules, s = _mid_band()
    step = decide_logged(s, rules, s.time, SetOrders((NEVER, LOW)))
    assert step.save.latches == (False, True) and step.rule_changes == ()


def test_an_edited_rule_is_latched_afresh_from_its_threshold():
    rules, s = _mid_band()
    widened = Order(AtMost(StoreValue(S0), 3 * Q, 9 * Q), SwitchMix(M0))
    step = decide_logged(s, rules, s.time, SetOrders((widened,)))
    assert step.save.latches == (False,)   # 7 is over its when of 3, whatever band it had
    assert step.rule_changes == ()   # a new order starting off is no change
    raised = Order(AtMost(StoreValue(S0), 7 * Q, 9 * Q), SwitchMix(M0))
    assert decide(s, rules, s.time, SetOrders((raised,))).latches == (True,)   # 7 is at its when of 7


def test_every_copy_of_a_kept_rule_takes_the_first_equal_old_rules_latch():
    rules, s = _mid_band()
    s = decide(s, rules, s.time, SetOrders((LOW, LOW)))
    assert s.latches == (True, True)
    assert decide(s, rules, s.time, SetOrders((NEVER, LOW, LOW, LOW))).latches == (False, True, True, True)


def test_a_rule_on_no_store_reports_no_level():
    rules, s = _world()
    now = Order(AfterTime(0), SwitchMix(M1))
    changes = decide_logged(s, rules, 10, SetOrders((LOW, now))).rule_changes
    assert [(c.order, c.on, c.level) for c in changes] == [(now, True, None)]
