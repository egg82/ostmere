"""An order card on the hands (a lane whose taps are never repeated, engine DESIGN.txt "REPEATING TAPS", "Who may
repeat") costs a latch turn and a landing every time its rule holds, so one hold has to cover more than one completion:
its band, release over value, is at least BAND_TAPS times what one completion puts in the store. A one-item band on a
one-item yield turned a rule on and off about once a minute while the roots drained, ~8,400 instants a game day."""
from collections.abc import Iterator

import pytest

from ashfall_app.opening.schema import Opening, load_opening
from tests.opening.edited import edited

BAND_TAPS = 2
"""The narrowest shipped band on a hands card is three completions (the roots rule at the opening, the clay rule six);
two is the least that lets a hold cover more than one tap."""
ROOTS_RULE = 'id = "roots", value = 3, release = 6 }'


def hands_bands(o: Opening) -> Iterator[tuple[str, int, int]]:
    """(tap card, band in items, items one completion adds to the store) of each non-chip at_most order card on the hands."""
    cards = {c.id: c for c in o.cards}
    for oc in o.order_cards:
        card = None if oc.tap_card is None else cards[oc.tap_card]
        if card is None or card.lane != "hands" or oc.chip is not None or oc.when.test != "at_most":
            continue
        yielded = sum(s.items for s in card.outcome.stores if s.store == oc.store)
        yield card.id, (oc.when.release or oc.when.value) - oc.when.value, yielded


def test_the_hands_bands_are_read_and_include_the_roots_rules():
    found = list(hands_bands(load_opening()))
    assert {"forage", "dig_clay"} <= {tap for tap, _, _ in found}
    assert all(yielded > 0 for _, _, yielded in found)


def test_every_shipped_hands_band_covers_more_than_one_completion():
    narrow = [(tap, band, yielded) for tap, band, yielded in hands_bands(load_opening()) if band < BAND_TAPS * yielded]
    assert narrow == []


def test_a_planted_narrow_band_fails_the_loader():
    with pytest.raises(ValueError, match="band"):
        edited(data=lambda part: part.replace(ROOTS_RULE, 'id = "roots", value = 3, release = 4 }'))


def test_the_plant_changes_the_card_it_names():
    wide = edited(data=lambda part: part.replace(ROOTS_RULE, 'id = "roots", value = 3, release = 7 }'))
    assert edited().order_cards != wide.order_cards
