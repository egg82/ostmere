"""LevelPays.speeds (api/CONTRACT.txt, "Skills"): the cards a level makes faster, read from the trigger that lands at
that level, so the page can show the level on the card it speeds up. A work entry names its card, a lane entry every
card on that lane; a rate, a cap or a find names none."""
import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def content() -> Content:
    o = load_opening()
    return Game(o, ruleset(o, "dev", 1)).content()


def speeds(content: Content) -> dict[tuple[str, int], list[str]]:
    return {(s.skill, lv.level): lv.speeds for s in content.skill_infos for lv in s.levels}


def test_a_work_level_names_its_card_and_a_lane_level_every_card_on_the_lane(content: Content):
    got = speeds(content)
    assert got[("woodcutting", 4)] == ["woodcutting"]
    rack = [c.card for c in content.card_infos if c.lane == "rack"]
    assert rack and got[("arcana", 2)] == rack


def test_a_rate_a_cap_or_a_find_names_no_card(content: Content):
    got = speeds(content)
    assert got[("cooking", 2)] == []   # a rate: the card makes more, it is not faster
    assert got[("woodcutting", 3)] == []   # a find


def test_every_named_card_is_a_card(content: Content):
    cards = {c.card for c in content.card_infos}
    named = [c for cs in speeds(content).values() for c in cs]
    assert len(named) > 50
    assert set(named) <= cards
