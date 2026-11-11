"""A chip's order card whose task is a card on a ruled lane (week-two-plan item 7), on fixtures/chipcure.toml merged
onto the opening alone. Nothing in the loader or the page needed to change: the card loads as day one's chip cards do,
the rule it makes runs the cure on the lane at the chip's instant, and a card naming a task no lane has is refused."""
from pathlib import Path

import pytest

from ashfall_app.engine import CardId, Order, Rules, SetOrders, StoreId, TapCard, advance, decide, new_save, units, value
from ashfall_app.engine.rates import tapped_cards
from ashfall_app.opening.convert import condition
from ashfall_app.opening.entries import OrderCardEntry
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "chipcure.toml"
HEAT, STOKE = StoreId("t_heat"), CardId("t_stoke")
CHIP_AT = 6_300
"""Warmth 10 falls 4 an hour: it reaches the chip's 3 after one hour and three quarters."""


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def edited(tmp_path: Path, old: str, new: str) -> Path:
    text = FIXTURE.read_text()
    assert text.count(old) == 1, old
    path = tmp_path / FIXTURE.name
    path.write_text(text.replace(old, new))
    return path


def chip_card(o: Opening) -> OrderCardEntry:
    return next(c for c in o.order_cards if c.chip == "t_cold")


def ruled(o: Opening) -> tuple[Rules, Order]:
    """The rules, and the rule the page makes of the chip's order card: its `when` and `then`."""
    card = chip_card(o)
    assert card.tap_card is not None
    return to_rules(o), Order(condition(card.when, set()), TapCard(CardId(card.tap_card)))


def played(rules: Rules, order: Order | None, t: int):
    s = advance(new_save(rules), rules, 0)
    if order is not None:
        s = decide(s, rules, 0, SetOrders((order,)))
    return advance(s, rules, t)


def test_a_chip_order_card_on_a_ruled_lane_loads():
    card = chip_card(load_with(FIXTURE))
    assert (card.chip, card.tap_card) == ("t_cold", "t_stoke")


def test_the_rule_runs_the_cure_on_the_lane_at_the_chips_instant():
    rules, order = ruled(load_with(FIXTURE))
    assert tapped_cards(played(rules, order, CHIP_AT - 1), rules) == ()
    assert tapped_cards(played(rules, order, CHIP_AT), rules) == (STOKE,)
    assert value(played(rules, order, CHIP_AT + 700), rules, HEAT, CHIP_AT + 700) > units(6)   # up to the rule's release


def test_without_the_rule_the_chip_is_not_cured():
    rules, _ = ruled(load_with(FIXTURE))
    assert value(played(rules, None, CHIP_AT + 7200), rules, HEAT, CHIP_AT + 7200) == 0


def test_a_chip_order_card_naming_a_card_no_lane_has_fails_the_loader(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown card t_missing"):
        load_with(edited(tmp_path, 'tap_card = "t_stoke"', 'tap_card = "t_missing"'))
