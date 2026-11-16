"""A card with the stake reach serves the store it fills and each reach's threshold, so its face can draw the next
(CardInfo.reach). The thresholds are the triggers', never retyped."""
import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def served() -> tuple[Content, list[int]]:
    o = load_opening()
    stops = [t.when.value for t in o.triggers if t.when.test == "at_least" and t.when.id == "track_laid"
             and t.when.subject_kind == "store"]
    return Game(o, ruleset(o, load_renames(), "dev", 1)).content(), stops


def test_every_card_with_a_reach_stake_serves_its_stops(served: tuple[Content, list[int]]):
    content, items = served
    stakes = [c for c in content.card_infos if c.reach is not None]
    assert len(items) >= 5 and len(stakes) >= 7, "the track's cards serve no reach: the check is blind"
    per_item = content.scales.quantity_per_item
    for c in stakes:
        assert c.reach is not None
        assert c.reach.store == "track_laid"
        assert c.reach.stops == [n * per_item for n in items], c.card


def test_a_card_without_the_stake_serves_none(served: tuple[Content, list[int]]):
    content, _ = served
    assert [c.card for c in content.card_infos if c.reach is None and c.card.endswith("field_track")] == []
    assert next(c for c in content.card_infos if c.card == "make_spear").reach is None
