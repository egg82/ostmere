"""An order card at_least on the store a staged build takes, tapping that build, loads: one order covers every stage
(engine DESIGN.txt, "ORDER CARD ON A STAGED BUILD"). The build is day four's three-stage shed, edited in a copy; the
control that must fail taps a card that does not take the store."""
from pathlib import Path

import pytest

from ashfall_app.engine import CardId
from ashfall_app.opening.schema import CHAPTERS, DAY_FOUR, OPENING, Opening, load_opening

TEXT = DAY_FOUR.read_text()
ORDER = """[[order_cards]]
store = "damp_wood"
tap_card = "{card}"
when = {{ test = "at_least", subject_kind = "store", id = "damp_wood", value = 12, release = 6 }}

[text]
"""


def loaded(tmp_path: Path, card: str) -> Opening:
    assert TEXT.count("\n[text]\n") == 1 and "[[order_cards]]" not in TEXT
    path = tmp_path / DAY_FOUR.name
    path.write_text(TEXT.replace("[text]\n", ORDER.format(card=card), 1))
    return load_opening(OPENING, tuple(path if c == DAY_FOUR else c for c in CHAPTERS))


def test_an_at_least_order_card_taps_a_three_stage_build(tmp_path: Path):
    o = loaded(tmp_path, "woodshed")
    shed = next(c for c in o.cards if c.id == "woodshed")
    assert shed.cap == 3
    assert [(oc.tap_card, oc.when.test) for oc in o.order_cards if oc.store == "damp_wood"
            and oc.tap_card == CardId("woodshed")] == [("woodshed", "at_least")]


def test_an_at_least_order_card_on_a_card_that_does_not_take_the_store_fails(tmp_path: Path):
    with pytest.raises(Exception, match="does not take damp_wood"):
        loaded(tmp_path, "forage")
