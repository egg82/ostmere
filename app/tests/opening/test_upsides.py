"""The loader's upside check (opening/upside_checks.py): every card the player taps has an upside_key, but the listed
plain gatherers and the town twins of them. Each refusal is a card merged onto the opening alone, beside a control
that passes."""
from typing import Any

import pytest

from ashfall_app.opening.chapters import merge
from ashfall_app.opening.schema import Chapter, Opening, load_opening
from ashfall_app.opening.upside_checks import BARE, check_upsides

CARD: dict[str, Any] = {"id": "t_card", "presentation": "action", "label_key": "t_c", "work_s": 60}


def merged(*cards: dict[str, Any]) -> Opening:
    return merge(load_opening(chapters=()), Chapter.model_validate({"version": 1, "cards": list(cards)}))


def test_an_action_card_without_an_upside_is_refused_by_name():
    with pytest.raises(ValueError, match="cards t_card: are tapped by the player"):
        check_upsides(merged(CARD))


def test_every_such_card_is_named_at_once():
    with pytest.raises(ValueError, match="cards t_card, t_two: "):
        check_upsides(merged(CARD, {**CARD, "id": "t_two"}))


def test_a_twin_without_an_upside_is_refused_unless_its_original_is_listed():
    twin = {**CARD, "id": "t_twin", "lane": "n1", "twin_of": "t_card"}
    with pytest.raises(ValueError, match="cards t_twin: "):
        check_upsides(merged({**CARD, "upside_key": "t_up"}, twin))


@pytest.mark.parametrize("passes", [{"upside_key": "t_up"}, {"presentation": "craft"}, {"presentation": "narrative"}])
def test_a_card_with_an_upside_or_not_tapped_passes(passes: dict[str, Any]):
    check_upsides(merged({**CARD, **passes}))


def test_a_listed_gatherer_and_its_twin_need_none():
    gatherer = sorted(BARE)[0]
    check_upsides(merged({**CARD, "id": gatherer}, {**CARD, "id": "t_twin", "lane": "n1", "twin_of": gatherer}))


def test_the_shipped_content_passes_and_lists_only_cards_that_exist():
    o = load_opening()
    check_upsides(o)
    assert BARE <= {c.id for c in o.cards}
