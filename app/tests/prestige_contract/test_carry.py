"""The carry: XP stops at the earlier of the carry's end and the next phase's top, a click inside the window loses
nothing, one past it loses the overshoot, and levels counted across phases never fall."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    AtLeast, LineKey, Outcome, Prestige, SkillLevel, TriggerDef, TriggerId, advance, value,
)
from ashfall_app.engine.phases import at_top, level_counted, level_shown, phase_state, waiting_levels
from ashfall_app.engine.prestige import refusal
from prestige_world import CURVE, K, N1, P, SPAN, WOOD, at_second, click, rules, xp_now

R = rules()
CEILING = 2 * SPAN - 1


@given(window=st.integers(1, 1000), t=st.integers(0, 2000))
def test_xp_stops_at_the_earlier_of_the_carrys_end_and_the_next_top(window: int, t: int):
    r = rules(window)
    assert xp_now(at_second(r, t), r) == min(t, SPAN + window, CEILING)


def test_a_long_window_leaves_xp_below_the_next_top_and_one_click_waiting():
    waiting = at_second(R, 3000)
    assert xp_now(waiting, R) == CEILING
    assert phase_state(waiting, R, K).phase == 1 and at_top(waiting, R, K)
    assert level_shown(CURVE, P, 1, CEILING) == P.top_level
    assert waiting_levels(CURVE, P, 1, CEILING) == level_shown(CURVE, P, 2, CEILING) - 1 < P.top_level - 1
    assert refusal(waiting, R, Prestige(K, N1)) is None


def test_a_short_window_stops_xp_before_the_next_top():
    r = rules(100)
    assert xp_now(at_second(r, 399), r) == 399
    assert xp_now(at_second(r, 400), r) == 400
    assert xp_now(at_second(r, 3000), r) == 400
    assert at_top(at_second(r, 3000), r, K)


def test_the_skills_other_lines_run_on_after_its_xp_has_stopped():
    r = rules(100)
    early, late = at_second(r, 500), at_second(r, 1500)
    assert xp_now(early, r) == xp_now(late, r) == 400
    one = value(early, r, WOOD, 500)
    assert value(early, r, WOOD, 1500) - one == 1000 * 1000   # the standing action's make: 1000 a second


@given(delay=st.integers(0, 298))
def test_clicking_later_inside_the_window_ends_where_an_instant_clicker_does(delay: int):
    """P clicks at the top (second 300), Q `delay` seconds later; both read at second 599, inside the window."""
    p = click(at_second(R, SPAN), R, N1)
    q = click(at_second(R, SPAN + delay), R, N1)
    p, q = advance(p, R, 599), advance(q, R, 599)
    assert xp_now(p, R) == xp_now(q, R)
    assert level_shown(CURVE, P, 2, xp_now(p, R)) == level_shown(CURVE, P, 2, xp_now(q, R))
    assert phase_state(p, R, K).phase == phase_state(q, R, K).phase == 2


@given(delay=st.integers(101, 299))
def test_clicking_past_the_window_loses_the_xp_of_the_overshoot(delay: int):
    r = rules(100)
    instant = click(at_second(r, SPAN), r, N1)
    late = click(at_second(r, SPAN + delay), r, N1)
    when = SPAN + delay
    assert xp_now(advance(instant, r, when), r) - xp_now(late, r) == delay - 100


def test_levels_counted_across_phases_never_fall_at_a_click():
    for t in (SPAN, 450, 2000):
        waiting = at_second(R, t)
        xp_at = xp_now(waiting, R)
        before = level_counted(CURVE, P, 1, xp_at)
        clicked = click(waiting, R, N1)
        assert level_counted(CURVE, P, phase_state(clicked, R, K).phase, xp_now(clicked, R)) >= before


def test_a_trigger_on_a_skill_level_reads_levels_counted_across_phases():
    """Phase 1 shows at most level 3; counted level 4 is phase 2's level 2, 100 XP past the click's top."""
    trig = TriggerDef(TriggerId("t"), AtLeast(SkillLevel(K), 4, 4), Outcome(lines=(LineKey("t.fired"),)))
    r = replace(R, triggers=(trig,))
    top = at_second(r, SPAN)
    assert top.fired == (False,)
    assert at_second(r, 2000).fired == (False,)   # waiting in phase 1: counted level stays 3
    clicked = click(top, r, N1)
    assert advance(clicked, r, 399).fired == (False,)
    assert advance(clicked, r, 400).fired == (True,)
