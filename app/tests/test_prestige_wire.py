"""Prestige phases on the wire (api/CONTRACT.txt, "PRESTIGE PHASES"): SkillBar.prestige and Forecast.tops_out, each a
plain copy of the engine's, and null or empty for rules with no prestige."""
from dataclasses import replace

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from tests.engine.test_prestige_impl import A, B, GATHER, H, RULES, START


def wire_bar(save: e.Save, rules: e.Rules) -> w.SkillBar:
    return next(b for b in convert.view(save, e.view(save, rules)).skills if b.skill == GATHER)


def test_the_skill_bar_serves_the_engines_phase():
    s = e.advance(e.decide(START, RULES, 100 * H, e.Prestige(GATHER, A)), RULES, 100 * H)
    row = next(b for b in e.view(s, RULES).skills if b.skill == GATHER)
    assert row.prestige is not None
    p = wire_bar(s, RULES).prestige
    assert p == w.SkillPrestige(
        phase=2, level_counted=row.prestige.level_counted, at_top=False, waiting_levels=0,
        menu_nodes=[w.MenuNode(node=str(n.node), ranks_taken=n.ranks_taken, ranks=n.ranks,
                               before_value=n.before_value, after_value=n.after_value) for n in row.prestige.menu],
        undo_open=True, mastered=False, pick_owed=False, topped_at=None, picked=["a"], parked=[])
    assert p is not None and p.menu_nodes[0].ranks_taken == 1


def test_the_skill_bar_serves_the_nodes_picked_and_the_ranks_parked():
    clicked = e.decide(START, RULES, 100 * H, e.Prestige(GATHER, A))
    moved = e.decide(clicked, RULES, 100 * H, e.MovePick(GATHER, A, B))
    p = wire_bar(moved, RULES).prestige
    assert p is not None and (p.picked, p.parked) == ([], [w.ParkedPick(node="b", due=4)])


def test_the_forecast_serves_tops_out():
    f = convert.forecast(e.forecast(START, RULES, 200 * H))
    assert [t.model_dump() for t in f.tops_out] == [{"skill": "gather", "at": 100 * H}]


def test_no_prestige_serves_null_and_empty():
    plain = replace(RULES, prestige=None, nodes=())
    s = e.new_save(plain)
    dumped = wire_bar(s, plain).model_dump()
    assert "prestige" in dumped and dumped["prestige"] is None
    f = convert.forecast(e.forecast(s, plain, 200 * H)).model_dump()
    assert f["tops_out"] == [] and f["level_ups"]
