"""A card's need on a store a rule keeps (ashfall_app/opening/keep_checks.py): a draining store reaches the rule's
let-go level only for the moment the rule lets go, so a need at or past it is met only then, and a player the rules
carry finds the card unready at every return."""
import pytest

from ashfall_app.opening.keep_checks import check_kept_needs, kept_levels
from ashfall_app.opening.schema import load_opening
from tests.opening.edited import edited

STOCK_NEED = 'id = "roots", value = 12 },'


def test_the_kept_levels_are_read_and_include_the_roots():
    assert "roots" in kept_levels(load_opening())


def test_no_shipped_card_requires_a_kept_store_up_to_its_let_go():
    check_kept_needs(load_opening())


def test_a_planted_need_at_the_let_go_fails_the_loader():
    with pytest.raises(ValueError, match="take_stock: it requires 15 roots"):
        edited(data=lambda part: part.replace(STOCK_NEED, 'id = "roots", value = 15 },'))


def test_the_plant_changes_the_card_it_names():
    lower = edited(data=lambda part: part.replace(STOCK_NEED, 'id = "roots", value = 11 },'))
    assert edited().cards != lower.cards
