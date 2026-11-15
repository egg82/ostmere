"""Rule guards: directed tests for the mutants the blind suite let through (MUTANTS_guards.txt, "RUNS"). Each names the
row it kills; the blind test_guards_*_contract.py files are not edited."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AtLeast, AtMost, InvalidVerbError, LaneDef, LaneRules, OrderState, SetOrders, StoreValue, SwitchMix, TapCard,
    advance, decide, view,
)
from guards_world import (
    ALWAYS, DOWN, K, L, L2, RM, T, UP, W, at_least, at_most, cap_raise, guarded, kills, rules, start,
)
from test_guards_share_contract import HALF, _amounts, _chase, _mixes


@kills(3)
def test_a_guard_coming_on_inside_the_whens_band_leaves_the_when_latch_alone():
    """Statement 7: `when` is "W under 5, until over 15" and W is 3 + t; the guard "T is 10 or more" comes on at 10, when
    W is 13, past `when`'s value and short of its release. The `when` latch stays true (it lets go at 13) and the rule
    is paused, not waiting."""
    r = rules(t0=0, t_rate=1, w0=3, w_rate=1)
    s = start(r, (guarded(at_most(5, 15, W), SwitchMix(RM), at_least(10, 5)),))
    mid = advance(s, r, 11)
    assert view(mid, r).orders_on == (True,)
    assert view(mid, r).order_states == (OrderState.PAUSED,)
    assert view(advance(s, r, 14), r).order_states == (OrderState.WAITING,)


@kills(8)
def test_setting_a_rule_whose_guard_already_holds_spends_no_firing():
    """Statement 11: a guard set from its threshold is latched when the rule is set, so no latch change is left to
    fire; with one firing an instant, setting it must not suspend the instant."""
    r = rules(t0=10, max_firings=1)
    s = start(r, ())
    after = decide(s, r, 0, SetOrders((guarded(ALWAYS, TapCard(K), at_least(5, 4)),)))
    assert after.latches[0].unless == (True,)
    assert after.cascade_count == 0


@kills(13)
@pytest.mark.parametrize("b", [HALF, 3000, 7000, 9600])
def test_an_at_most_share_guard_reads_the_whole_items_of_a_fractional_cap(b: int):
    """Statement 9: with T's cap 10.5 items an at-most share guard reads the 10 whole items, as the table gives."""
    value, release = _amounts(False, b, 10)
    r = rules(t0=10, cap=10, triggers=(cap_raise(0, 10_500),))
    s = start(r, (guarded(ALWAYS, SwitchMix(DOWN), AtMost(StoreValue(T), b, b, value_of_cap=True, release_of_cap=True)),),
              active=UP)
    assert _mixes(r, s, 30) == _chase(False, value, release, 10, 30)


@kills(21)
def test_a_guard_reading_lane_rules_is_refused_on_a_ruled_lane():
    """Statement 3: LaneRules is a trigger's alone. On a lane that is ruled the subject is known, so only the guard
    check can refuse it."""
    r = replace(rules(), lanes=(LaneDef(L), LaneDef(L2, True)))
    s = start(r, ())
    bad = AtLeast(LaneRules(L2), 1, 1)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SetOrders((guarded(ALWAYS, TapCard(K), bad),)))
