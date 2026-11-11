"""The loader's prestige bar (opening/prestige.check_phase_spans): no carry window longer than the ordinary absence, and
no skill's phase spanned inside one by a full share of its fastest runner."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    ActionId, CardDef, CardId, PacingCurve, PrestigeDef, Rules, SkillDef, SkillId, StandingDef, StoreDef, StoreId,
    per_hour, units,
)
from ashfall_app.engine.nodes import ORDINARY_ABSENCE_S
from ashfall_app.opening.checks import check_content
from ashfall_app.opening.convert import build_rules
from ashfall_app.opening.prestige import PrestigeEntry, check_phase_spans
from ashfall_app.opening.schema import Opening

GATHER = SkillId("gather")
RULES = Rules(
    stores=(StoreDef(StoreId("wood"), units(10)),), skills=(SkillDef(GATHER),),
    standing=(StandingDef(ActionId("pick"), skill=GATHER, xp_per_hour=per_hour(1)),),
    curve=PacingCurve((units(40), units(96), units(200))),
    cards=(CardDef(CardId("chop"), 60, skill=GATHER, xp_per_hour=per_hour(2)),),
    prestige=PrestigeDef(top_level=3, carry_window_s=ORDINARY_ABSENCE_S, menu_size=2),
)
"""A phase spans units(96): exactly the ordinary absence at chop's 2 XP per hour."""


def test_a_phase_exactly_an_ordinary_absence_long_passes():
    check_phase_spans(RULES)


@pytest.mark.parametrize("rules", [
    replace(RULES, cards=(replace(RULES.cards[0], xp_per_hour=per_hour(2) + 1),)),
    replace(RULES, standing=(replace(RULES.standing[0], xp_per_hour=per_hour(3)),)),
], ids=["card", "standing"])
def test_a_runner_that_spans_a_phase_inside_an_absence_is_refused(rules: Rules):
    with pytest.raises(ValueError, match="gather"):
        check_phase_spans(rules)


def test_a_carry_window_longer_than_the_ordinary_absence_is_refused():
    assert RULES.prestige is not None
    with pytest.raises(ValueError, match="carry_window_s"):
        check_phase_spans(replace(RULES, prestige=replace(RULES.prestige, carry_window_s=ORDINARY_ABSENCE_S + 1)))


def test_the_shipped_content_has_prestige_and_passes(shipped_opening: Opening):
    assert shipped_opening.prestige is not None
    check_phase_spans(build_rules(shipped_opening))


def test_the_load_runs_the_check(shipped_opening: Opening):
    long_window = PrestigeEntry(top_level=2, carry_window_s=ORDINARY_ABSENCE_S + 1, menu_size=2)
    with pytest.raises(ValueError, match="carry_window_s"):
        check_content(shipped_opening.model_copy(update={"prestige": long_window}))
