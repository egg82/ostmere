"""Invariant 7: values stay in [0, cap], XP in [0, last threshold], levels never decrease."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    CardShare, Flow, Mix, SaveMix, StoreDef, SwitchMix, advance, decide, level, level_for, new_save, segment, value,
    xp,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, play, probe_times, scenario_st, store_id, few, Scenario


@few(10)
@given(sc=scenario_st(), extra=st.lists(st.integers(0, 200_000), max_size=6))
def test_values_within_bounds_everywhere(sc: Scenario, extra: list[int]):
    """Invariant 7 (bounds): 0 <= value <= cap and 0 <= xp <= last threshold at event times, +/- 1, and far out (600k s)."""
    s = play(sc)
    top = sc.rules.curve.thresholds[-1]
    for t in probe_times(s, sc.rules, sc.offsets + tuple(extra)) + [s.time + 600_000]:
        for sd in sc.rules.stores:
            assert 0 <= value(s, sc.rules, sd.id, t) <= sd.cap, (sd.id, t)
        for sk in sc.rules.skills:
            assert 0 <= xp(s, sc.rules, sk.id, t) <= top, (sk.id, t)


@given(sc=scenario_st(), extra=st.lists(st.integers(0, 200_000), max_size=6))
def test_levels_never_decrease(sc: Scenario, extra: list[int]):
    """Invariant 7 (bounds): level is non-decreasing in t, and equals level_for(curve, xp) with max level reached
    only at the XP cap."""
    s = play(sc)
    ts = probe_times(s, sc.rules, sc.offsets + tuple(extra))
    for sk in sc.rules.skills:
        prev = 0
        for t in ts:
            lv = level(s, sc.rules, sk.id, t)
            assert lv >= prev and 1 <= lv <= len(sc.rules.curve.thresholds) + 1
            assert lv == level_for(sc.rules.curve, xp(s, sc.rules, sk.id, t))
            prev = lv


@given(sc=scenario_st(), extra=st.lists(st.integers(0, 200_000), min_size=1, max_size=4))
def test_rate_never_pushes_past_a_bound(sc: Scenario, extra: list[int]):
    """Invariant 7 (bounds): a store at 0 never has a negative segment rate; one at its cap never a positive one."""
    s = play(sc)
    for t in probe_times(s, sc.rules, tuple(extra)):
        a = advance(s, sc.rules, t)
        for sd in sc.rules.stores:
            seg = segment(a, sc.rules, sd.id)
            if seg.start_value == 0:
                assert seg.rate >= 0
            if seg.start_value == sd.cap:
                assert seg.rate <= 0


@given(st.integers(0, 3_000_000), st.integers(1, 5000), st.integers(1, 6))
def test_overshoot_of_the_last_partial_second_is_clamped(v0: int, rate: int, hours: int):
    """Invariant 7 (bounds): a maker whose rate does not divide the room stops exactly at cap, never above it."""
    cap = Q
    v0 = min(v0, cap)
    rules = make_rules([StoreDef(store_id(0), cap, v0)], [card(0, makes=(Flow(store_id(0), rate),))])
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(mix_id(0), (CardShare(card_id(0), 10_000),))))
    s = decide(s, rules, 0, SwitchMix(mix_id(0)))
    for t in (hours * 3600, hours * 3600 + 1, 10_000_000):
        assert 0 <= value(s, rules, store_id(0), t) <= cap
    assert value(s, rules, store_id(0), 10_000_000) == cap
