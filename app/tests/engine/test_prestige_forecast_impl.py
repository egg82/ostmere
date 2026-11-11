"""The forecast under prestige phases (engine forecast.py): each skill's top-out at the instant the engine sets its
topped_at, level-ups that stop at the phase's top, and no top-out for a skill at its top, mastered, or under rules
with no prestige."""
from dataclasses import replace

from ashfall_app.engine import Prestige, advance, decide, forecast, new_save
from ashfall_app.engine.phases import phase_state
from tests.engine.test_prestige_impl import A, CRAFT, GATHER, H, RULES, START

HORIZON = 500 * H


def test_each_top_out_is_the_instant_the_engine_tops_the_skill_out():
    f = forecast(START, RULES, HORIZON)
    later = advance(START, RULES, HORIZON)
    assert f.until == HORIZON
    assert set(f.tops_out) == {GATHER, CRAFT}
    for skill in (GATHER, CRAFT):
        assert f.tops_out[skill] == phase_state(later, RULES, skill).topped_at
    assert f.tops_out[GATHER] == 100 * H
    assert GATHER not in forecast(START, RULES, 100 * H - 1).tops_out


def test_level_ups_end_at_the_phases_top():
    assert forecast(START, RULES, HORIZON).level_ups[GATHER] == (10 * H, 40 * H, 100 * H)
    plain = replace(RULES, prestige=None, nodes=())
    assert forecast(new_save(plain), plain, HORIZON).level_ups[GATHER] == (10 * H, 40 * H, 100 * H, 200 * H)


def test_a_click_forecasts_the_next_phases_top_and_its_levels():
    clicked = decide(START, RULES, 100 * H, Prestige(GATHER, A))
    f = forecast(clicked, RULES, HORIZON)
    assert f.tops_out[GATHER] == 200 * H
    assert f.level_ups[GATHER] == (110 * H, 140 * H, 200 * H)


def test_no_top_out_at_the_top_when_mastered_or_without_prestige():
    at_top = advance(START, RULES, 100 * H)
    assert GATHER not in forecast(at_top, RULES, HORIZON).tops_out
    craft_only = replace(RULES, nodes=tuple(n for n in RULES.nodes if n.skill == CRAFT))
    assert set(forecast(new_save(craft_only), craft_only, HORIZON).tops_out) == {CRAFT}
    plain = replace(RULES, prestige=None, nodes=())
    assert forecast(new_save(plain), plain, HORIZON).tops_out == {}
