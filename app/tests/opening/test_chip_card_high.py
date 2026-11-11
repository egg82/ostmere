"""A chip shown while its store is high (an at_least chip) takes an order card too, on fixtures/chipload.toml merged
onto the opening alone: the card's `when` is the chip's and its task takes the store, so the rule spends what made the
chip show. The loader accepts it, the rule runs the cure on a ruled lane at the chip's instant, and a card whose task
does not take the store is refused."""
from pathlib import Path

import pytest

from ashfall_app.engine import CardId, Order, SetOrders, StoreId, TapCard, advance, decide, new_save, units, value
from ashfall_app.engine.rates import tapped_cards
from ashfall_app.opening.convert import condition
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "chipload.toml"
LOAD, SHOVEL = StoreId("t_load"), CardId("t_shovel")
CHIP_AT = 7_200
"""Load 0 rises 4 an hour: it reaches the chip's 8 after two hours."""


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def test_the_chips_order_card_loads():
    card = next(c for c in load_with(FIXTURE).order_cards if c.chip == "t_laden")
    assert (card.when.test, card.tap_card) == ("at_least", "t_shovel")


def test_the_rule_runs_the_cure_on_the_lane_at_the_chips_instant():
    o = load_with(FIXTURE)
    rules = to_rules(o)
    card = next(c for c in o.order_cards if c.chip == "t_laden")
    s = decide(advance(new_save(rules), rules, 0), rules, 0, SetOrders((Order(condition(card.when, set()), TapCard(SHOVEL)),)))
    assert tapped_cards(advance(s, rules, CHIP_AT - 1), rules) == ()
    at = advance(s, rules, CHIP_AT)
    assert tapped_cards(at, rules) == (SHOVEL,)
    done = CHIP_AT + 601
    assert value(advance(s, rules, done), rules, LOAD, done) < units(1)   # the shovel took what showed the chip


def test_a_chip_card_whose_task_does_not_take_the_store_fails_the_loader(tmp_path: Path):
    text = FIXTURE.read_text()
    old = 'inputs = [{ store = "t_load", items = 8 }]'
    assert text.count(old) == 1
    path = tmp_path / FIXTURE.name
    path.write_text(text.replace(old, ""))
    with pytest.raises(ValueError, match="does not take t_load"):
        load_with(path)
