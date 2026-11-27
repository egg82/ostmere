"""Directed tests for survivors of the or_else mutation run (tools/mutants/or_else/): what the blind suite left open."""
from ashfall_app.engine import (
    AfterTime, AtMost, Outcome, QUANTITY_SCALE as Q, StoreValue, TapCard, TriggerDef, TriggerId, advance,
)
from or_else_world import A1, A2, A3, ALWAYS, T, lanes, rule, rules, start


def test_a_rule_that_keeps_an_action_keeps_a_guard_latch_held_inside_its_band():
    """Retiring A1 at 4 from [A1, A2, A3] while T is 4: the guard "T is 3 or less" (released above 4) latched true at 0
    and still holds, though a latch set afresh from T = 4 would read false. The rule stays paused to 5 and A2 starts
    there, not at 4."""
    chore = TriggerDef(TriggerId("chore"), AfterTime(4), Outcome(retire_orders=(A1,)))
    r = rules(t_rate=1, triggers=(chore,))
    guard = AtMost(StoreValue(T), 3 * Q, 4 * Q)
    s = start(r, (rule(ALWAYS, TapCard(A1), (TapCard(A2), TapCard(A3)), guard),))
    assert lanes(r, s, 7) == [None] * 5 + [A2] * 3
    assert advance(s, r, 4).latches == advance(s, r, 3).latches
