"""A carried bonus says what it does from served data (FeatureInfo.effect_key and change_bp), the cost text and changes
of the answer whose outcome unlocks it, never from text typed per bonus."""
import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.schema import CHAPTERS, load_opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def content() -> Content:
    o = load_opening(chapters=CHAPTERS)
    return Game(o, ruleset(o, "dev", 1)).content()


def test_a_feature_carries_the_cost_text_and_changes_of_its_answer(content: Content):
    answers = {(u.id): a for x in load_opening(chapters=CHAPTERS).offers for a in x.answers for u in a.outcome.unlocks
               if u.unlock_kind == "feature" and a.outcome.modifiers}
    served = {f.feature: f for f in content.feature_infos if f.effect_key}
    assert served and set(served) == set(answers)
    assert all(served[i].effect_key == a.cost_key and served[i].change_bp for i, a in answers.items())


def test_a_bonus_with_two_effects_serves_both_figures(content: Content):
    assert any(len(f.change_bp) == 2 for f in content.feature_infos if f.label_key)


def test_a_bonus_nothing_installs_effects_for_serves_none(content: Content):
    bare = [f for f in content.feature_infos if f.label_key and not f.effect_key]
    assert bare and all(f.change_bp == [] for f in bare)
