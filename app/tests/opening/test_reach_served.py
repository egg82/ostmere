"""A card with the stake reach serves the store it fills and each reach's threshold, so its face can draw the next
(CardInfo.reach). The thresholds are the triggers', never retyped."""
import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def served() -> tuple[Content, dict[str, list[int]]]:
    """The content, and each store's at_least thresholds in triggers, in items, by store id."""
    o = load_opening()
    stops: dict[str, list[int]] = {}
    for t in o.triggers:
        if t.when.test == "at_least" and t.when.subject_kind == "store" and t.when.id is not None:
            stops.setdefault(t.when.id, []).append(t.when.value)
    return Game(o, ruleset(o, load_renames(), "dev", 1)).content(), stops


STAKES = {"field_track": "track_laid", "sew_wraps": "wraps_sewn", "stack_windbreak": "windbreak"}
"""Each card with the stake reach, by its hands' id, and the store it fills (its town copies fill the same)."""


def test_every_card_with_a_reach_stake_serves_its_stops(served: tuple[Content, dict[str, list[int]]]):
    content, items = served
    stakes = [c for c in content.card_infos if c.reach is not None]
    assert len(items["track_laid"]) >= 5 and len(stakes) >= 8, "the cards serve no reach: the check is blind"
    per_item = content.scales.quantity_per_item
    for c in stakes:
        assert c.reach is not None
        store = next(s for card, s in STAKES.items() if c.card.endswith(card))
        assert c.reach.store == store, c.card
        assert c.reach.stops == [n * per_item for n in items[store]], c.card


def test_a_card_without_the_stake_serves_none(served: tuple[Content, dict[str, list[int]]]):
    content, _ = served
    assert [c.card for c in content.card_infos if c.reach is None and c.card.endswith("field_track")] == []
    assert next(c for c in content.card_infos if c.card == "make_spear").reach is None
