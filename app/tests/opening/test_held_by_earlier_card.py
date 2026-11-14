"""A chapter gives an earlier card the entries it holds while running (schema.Chapter.while_running): a side the
chapter declares, raised by a card an earlier file shipped, after any entries the card holds. The merge refuses an
unknown card and an entry on a side the card already holds; the merged card reaches the engine's rules with them."""
import pytest

from ashfall_app.engine import CardId, SideId, WhileRunning
from ashfall_app.opening.chapters import merge
from ashfall_app.opening.schema import Chapter, load_opening, to_rules

CARD = "gather_wood"
"""A card of the opening's own file."""


def chapter(card: str, side: str = "t_gap") -> Chapter:
    return Chapter.model_validate({
        "version": 1,
        "sides": [{"id": side, "label_key": f"t_side_{side}", "base": 4}],
        "while_running": {card: [{"side": side, "amount_bp": 5000}]},
        "text": {f"t_side_{side}": "Gap"},
    })


def test_the_earlier_card_holds_the_entry_in_the_rules():
    rules = to_rules(merge(load_opening(chapters=()), chapter(CARD)))
    card = next(c for c in rules.cards if c.id == CardId(CARD))
    assert card.while_running == (WhileRunning(SideId("t_gap"), 5000),)
    others = [c.id for c in rules.cards if c.while_running and c.id != CardId(CARD)]
    assert others == []


def test_an_unknown_card_fails_the_merge():
    with pytest.raises(ValueError, match="unknown card ghost"):
        merge(load_opening(chapters=()), chapter("ghost"))


def test_a_later_chapter_adds_a_second_side_after_the_first():
    twice = merge(merge(load_opening(chapters=()), chapter(CARD)), chapter(CARD, "t_wall"))
    card = next(c for c in to_rules(twice).cards if c.id == CardId(CARD))
    assert card.while_running == (WhileRunning(SideId("t_gap"), 5000), WhileRunning(SideId("t_wall"), 5000))


def test_an_entry_on_a_side_the_card_already_holds_fails_the_merge():
    once = merge(load_opening(chapters=()), chapter(CARD))
    again = chapter(CARD).model_copy(update={"sides": [], "text": {}})
    with pytest.raises(ValueError, match=f"card {CARD} already holds an entry on \\['t_gap'\\]"):
        merge(once, again)
