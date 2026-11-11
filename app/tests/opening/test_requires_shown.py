"""A card is never shown waiting on a story beat: each `requires` entry of a card either appears in the card's needs
(engine `store_need`) or is a progress condition the card's own blocker names; an `unlocked` require is neither, so
the beat that sets it must open the card instead."""
from dataclasses import replace

from ashfall_app.engine import CardDef, Unlock, UnlockKind, store_need
from ashfall_app.engine.orders import AtLeast, Unlocked
from tests.opening.playthrough import opening_rules


def hidden_requires(cards: tuple[CardDef, ...]) -> list[str]:
    """`card: require` for each require of a card that its needs list cannot show and that is an unlock flag."""
    return [f"{c.id}: {cond}" for c in cards for cond in c.requires
            if store_need(cond) is None and isinstance(getattr(cond, "subject", None), Unlocked)]


def test_no_card_requires_a_story_flag_its_needs_cannot_show():
    cards = tuple(opening_rules().cards)
    assert any(c.requires for c in cards), "checked no card with a require: the check is blind"
    assert hidden_requires(cards) == []


def test_the_check_can_fail():
    stock = next(c for c in opening_rules().cards if c.id == "take_stock")
    prints = AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, "prints")), 1, 1)
    planted = replace(stock, requires=(*stock.requires, prints))
    assert hidden_requires((planted,)) == [f"take_stock: {prints}"]
