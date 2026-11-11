"""phases.py's pure functions, from their docstrings: the span and tops, the ceiling, the carry's end, the shown and
counted levels, and the levels waiting. Properties run over random curves and phases."""
import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import DrawFn

from ashfall_app.engine import PacingCurve, PhaseState, PrestigeDef, level_for, xp_for
from ashfall_app.engine.phases import (
    accrues, carry_ends_at, level_counted, level_shown, phase_top, span, waiting_levels, xp_ceiling,
)

Draw = DrawFn


@st.composite
def worlds(draw: Draw) -> tuple[PacingCurve, PrestigeDef]:
    n = draw(st.integers(2, 6))
    steps = draw(st.lists(st.integers(1, 1000), min_size=n, max_size=n))
    thresholds: list[int] = []
    for step in steps:
        thresholds.append((thresholds[-1] if thresholds else 0) + step)
    top = draw(st.integers(2, n + 1))
    return PacingCurve(tuple(thresholds)), PrestigeDef(top, draw(st.integers(1, 10_000)), draw(st.sampled_from([2, 3])))


@st.composite
def reads(draw: Draw) -> tuple[PacingCurve, PrestigeDef, int, int]:
    """A world, a phase, and an XP a save in that phase can hold: from the previous top up to the ceiling."""
    curve, p = draw(worlds())
    phase = draw(st.integers(1, 5))
    xp = draw(st.integers(phase_top(curve, p, phase - 1) if phase > 1 else 0, xp_ceiling(curve, p, phase)))
    return curve, p, phase, xp


@given(worlds())
def test_span_is_the_xp_to_the_top_level(w: tuple[PacingCurve, PrestigeDef]):
    curve, p = w
    assert span(curve, p) == xp_for(curve, p.top_level) > 0


@given(worlds(), st.integers(1, 50))
def test_phase_top_is_phase_spans(w: tuple[PacingCurve, PrestigeDef], phase: int):
    curve, p = w
    assert phase_top(curve, p, phase) == phase * span(curve, p)


@given(worlds(), st.integers(-5, 0))
def test_a_phase_below_one_is_a_value_error(w: tuple[PacingCurve, PrestigeDef], phase: int):
    curve, p = w
    with pytest.raises(ValueError):
        phase_top(curve, p, phase)
    with pytest.raises(ValueError):
        xp_ceiling(curve, p, phase)


@given(worlds(), st.integers(1, 50))
def test_the_ceiling_is_just_below_the_next_phases_top(w: tuple[PacingCurve, PrestigeDef], phase: int):
    curve, p = w
    assert xp_ceiling(curve, p, phase) == phase_top(curve, p, phase + 1) - 1
    assert xp_ceiling(curve, p, phase) >= phase_top(curve, p, phase)


@given(worlds(), st.integers(1, 50))
def test_without_prestige_the_ceiling_is_the_last_threshold(w: tuple[PacingCurve, PrestigeDef], phase: int):
    curve, _ = w
    assert xp_ceiling(curve, None, phase) == curve.thresholds[-1]


@given(worlds(), st.integers(0, 10**6))
def test_the_carry_ends_a_window_after_topping_out(w: tuple[PacingCurve, PrestigeDef], topped: int):
    _, p = w
    assert carry_ends_at(p, PhaseState(topped_at=topped)) == topped + p.carry_window_s
    assert carry_ends_at(p, PhaseState()) is None


@given(worlds(), st.integers(0, 10**6), st.integers(0, 2 * 10**6))
def test_accrual_stops_exactly_at_the_carrys_end(w: tuple[PacingCurve, PrestigeDef], topped: int, t: int):
    _, p = w
    state = PhaseState(topped_at=topped)
    assert accrues(p, state, t) is (t < topped + p.carry_window_s)
    assert accrues(p, state, topped + p.carry_window_s - 1) is True
    assert accrues(p, state, topped + p.carry_window_s) is False


@given(worlds(), st.integers(0, 2 * 10**6))
def test_accrual_runs_below_the_top_and_without_prestige(w: tuple[PacingCurve, PrestigeDef], t: int):
    _, p = w
    assert accrues(p, PhaseState(), t) is True
    assert accrues(None, PhaseState(topped_at=0), t) is True


@given(reads())
def test_level_shown_reads_the_curve_from_level_one_in_each_phase(r: tuple[PacingCurve, PrestigeDef, int, int]):
    curve, p, phase, xp = r
    shown = level_shown(curve, p, phase, xp)
    below = phase_top(curve, p, phase - 1) if phase > 1 else 0
    assert 1 <= shown <= p.top_level
    assert shown == level_for(curve, min(xp, phase_top(curve, p, phase)) - below)
    assert (shown == p.top_level) is (xp >= phase_top(curve, p, phase))


@given(reads(), st.integers(0, 1000))
def test_level_shown_is_monotone_in_xp_within_a_phase(r: tuple[PacingCurve, PrestigeDef, int, int], more: int):
    curve, p, phase, xp = r
    later = min(xp + more, xp_ceiling(curve, p, phase))
    assert level_shown(curve, p, phase, later) >= level_shown(curve, p, phase, xp)


@given(worlds(), st.integers(0, 10**5))
def test_level_shown_without_prestige_is_level_for(w: tuple[PacingCurve, PrestigeDef], xp: int):
    curve, _ = w
    assert level_shown(curve, None, 1, xp) == level_for(curve, xp)
    assert level_counted(curve, None, 1, xp) == level_for(curve, xp)


@given(reads())
def test_level_counted_adds_the_levels_of_the_phases_behind(r: tuple[PacingCurve, PrestigeDef, int, int]):
    curve, p, phase, xp = r
    assert level_counted(curve, p, phase, xp) == (phase - 1) * (p.top_level - 1) + level_shown(curve, p, phase, xp)


@given(reads())
def test_level_counted_never_falls_at_a_click(r: tuple[PacingCurve, PrestigeDef, int, int]):
    """The same XP read in the next phase (what a click does) counts as much, and exactly as much at the top itself."""
    curve, p, phase, _ = r
    top = phase_top(curve, p, phase)
    for xp in (top, (top + xp_ceiling(curve, p, phase)) // 2, xp_ceiling(curve, p, phase)):
        assert level_counted(curve, p, phase + 1, xp) >= level_counted(curve, p, phase, xp)
    assert level_counted(curve, p, phase + 1, top) == level_counted(curve, p, phase, top)


@given(reads())
def test_waiting_levels_are_what_a_click_would_land_at(r: tuple[PacingCurve, PrestigeDef, int, int]):
    curve, p, phase, xp = r
    waiting = waiting_levels(curve, p, phase, xp)
    if xp >= phase_top(curve, p, phase):
        assert waiting == level_shown(curve, p, phase + 1, xp) - 1
    else:
        assert waiting == 0
    assert 0 <= waiting <= p.top_level - 1


@given(worlds())
def test_a_long_wait_leaves_levels_waiting_below_the_new_top(w: tuple[PacingCurve, PrestigeDef]):
    """At the ceiling the new phase would start below its own top, so one absence leaves one click waiting."""
    curve, p = w
    ceiling = xp_ceiling(curve, p, 1)
    assert waiting_levels(curve, p, 1, ceiling) == level_shown(curve, p, 2, ceiling) - 1
    assert level_shown(curve, p, 2, ceiling) < p.top_level
