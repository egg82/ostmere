"""Invariant 8 (exact event times) and the exact-arithmetic primitives the event times are built from."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, CardShare, EventKind, Flow, Mix, QUANTITY_SCALE, RATE_SCALE, SaveMix, Segment, StoreDef,
    SwitchMix, ceil_div, decide, level_for, new_save, next_event, per_hour, reach_time, segment, units, value,
    value_at, xp_for,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, store_id

import pytest


def _run_one_card(cap: int, v0: int, make: int | None = None, cost: int | None = None, t0: int = 0):
    makes = (Flow(store_id(0), make),) if make else ()
    costs = (Flow(store_id(0), cost),) if cost else ()
    rules = make_rules([StoreDef(store_id(0), cap, v0)], [card(0, makes=makes, costs=costs)])
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(mix_id(0), (CardShare(card_id(0), BP),))))
    return rules, decide(s, rules, t0, SwitchMix(mix_id(0)))


@given(v=st.integers(1, 40 * Q), k=st.integers(1, 30_000), t0=st.integers(0, 10_000))
def test_drain_reaches_zero_at_ceiling_time(v: int, k: int, t0: int):
    """Invariant 8 (exact event times): value v, rate -k: empty at t0 + ceil(v/k), still above 0 one second earlier."""
    rules, s = _run_one_card(50 * Q, v, cost=k, t0=t0)
    expected = t0 + -(-v // k)
    e = next_event(s, rules)
    assert e is not None and e.kind == EventKind.STORE_LIMIT and e.time == expected
    assert value(s, rules, store_id(0), expected - 1) > 0
    assert value(s, rules, store_id(0), expected) == 0
    assert value(s, rules, store_id(0), expected + 5000) == 0
    seg = segment(s, rules, store_id(0))
    assert seg.rate == -k and seg.limit == 0


@given(room=st.integers(1, 40 * Q), k=st.integers(1, 30_000), t0=st.integers(0, 10_000))
def test_fill_reaches_cap_at_ceiling_time(room: int, k: int, t0: int):
    """Invariant 8 (exact event times): the mirror: a maker reaches the cap at t0 + ceil(room/k) and the overshoot
    of the final partial second is clamped (value == cap, never above)."""
    cap = 50 * Q
    rules, s = _run_one_card(cap, cap - room, make=k, t0=t0)
    expected = t0 + -(-room // k)
    e = next_event(s, rules)
    assert e is not None and e.kind == EventKind.STORE_LIMIT and e.time == expected
    assert value(s, rules, store_id(0), expected - 1) < cap
    assert value(s, rules, store_id(0), expected) == cap
    assert value(s, rules, store_id(0), expected + 5000) == cap


@given(a=st.integers(-10**12, 10**12), b=st.integers(1, 10**9))
def test_ceil_div_is_exact(a: int, b: int):
    """Invariant 8 (exact event times): ceil_div is the exact integer ceiling for any sign of a."""
    c = ceil_div(a, b)
    assert c * b >= a > (c - 1) * b


@given(a=st.integers(-100, 100), b=st.integers(-100, 0))
def test_ceil_div_rejects_non_positive_divisor(a: int, b: int):
    """Invariant 8 (exact event times): ceil_div raises ValueError for b <= 0."""
    with pytest.raises(ValueError):
        ceil_div(a, b)


@given(st.integers(0, 10**6))
def test_unit_conversions(n: int):
    """Invariant 8 (exact event times): units/per_hour are exact scalings and the scales are consistent."""
    assert units(n) == n * QUANTITY_SCALE and per_hour(n) == n * RATE_SCALE
    assert QUANTITY_SCALE == RATE_SCALE * 3600


def _segment(start: int, v0: int, rate: int, room: int) -> Segment:
    return Segment(start, v0, rate, v0 + room if rate > 0 else v0 - min(room, v0))


_seg = st.builds(
    _segment, st.integers(0, 1000), st.integers(0, 10**9),
    st.integers(1, 10**6).flatmap(lambda r: st.sampled_from([r, -r])), st.integers(0, 10**9))


@given(seg=_seg, dt=st.integers(0, 10**7))
def test_value_at_is_linear_then_clamped(seg: Segment, dt: int):
    """Invariants 6, 7 (linear, bounds): value_at is start_value + rate*dt, held at the limit in the direction of
    motion."""
    assert seg.limit is not None  # _seg always sets one
    raw = seg.start_value + seg.rate * dt
    want = min(raw, seg.limit) if seg.rate > 0 else max(raw, seg.limit)
    assert value_at(seg, seg.start + dt) == want


@given(seg=_seg)
def test_reach_time_is_the_first_second(seg: Segment):
    """Invariant 8 (exact event times): reach_time(seg, limit) is the first integer t with value_at(t) at the limit."""
    assert seg.limit is not None  # _seg always sets one
    t = reach_time(seg, seg.limit)
    assert t is not None and t >= seg.start
    assert value_at(seg, t) == seg.limit
    if t > seg.start:
        assert value_at(seg, t - 1) != seg.limit


@given(seg=_seg)
def test_reach_time_is_none_for_unreachable_targets(seg: Segment):
    """Invariant 8 (exact event times): a target behind the motion is never reached; at-target returns seg.start."""
    behind = seg.start_value - seg.rate // abs(seg.rate)
    assert reach_time(seg, behind) is None
    assert reach_time(seg, seg.start_value) == seg.start


@given(st.lists(st.integers(1, 1000), min_size=1, max_size=8), st.integers(0, 10**5))
def test_level_for_and_xp_for(steps: list[int], extra: int):
    """Invariant 7 (bounds, levels): level_for is 1 + thresholds <= xp, monotone, 1 at 0, max at the XP cap, and
    xp_for inverts it; xp_for raises ValueError outside 1..len+1."""
    from ashfall_app.engine import PacingCurve
    th = tuple(sum(steps[: i + 1]) for i in range(len(steps)))
    curve = PacingCurve(th)
    assert level_for(curve, 0) == 1 and level_for(curve, th[-1]) == len(th) + 1
    x = extra % (th[-1] + 5)
    assert level_for(curve, x) == 1 + sum(1 for q in th if q <= x)
    assert xp_for(curve, 1) == 0
    for lv in range(2, len(th) + 2):
        assert xp_for(curve, lv) == th[lv - 2] and level_for(curve, xp_for(curve, lv)) == lv
    for bad in (0, len(th) + 2):
        with pytest.raises(ValueError):
            xp_for(curve, bad)
