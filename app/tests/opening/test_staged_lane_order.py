"""An at_least order card on a ruled lane tapping a staged card on that lane (week-three-plan item 8), on
fixtures/stagedlane.toml merged onto the opening alone. Nothing in the loader, the engine or the page needed to change:
the card loads as one on the hands does, the order lands every stage, and at the cap it is passed over and the lane goes
to its next rule. The page offers it under its store's line by the store alone (client/src/game/catalog.ts)."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    AfterTime, CardId, Order, Rules, Save, SetOrders, TapCard, advance, decide, new_save, view,
)
from ashfall_app.engine.rates import tapped_cards
from ashfall_app.opening.convert import condition
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "stagedlane.toml"
RAISE, SWEEP = CardId("t_raise"), CardId("t_sweep")


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def edited(tmp_path: Path, old: str, new: str) -> Path:
    text = FIXTURE.read_text()
    assert text.count(old) == 1, old
    path = tmp_path / FIXTURE.name
    path.write_text(text.replace(old, new))
    return path


def lane_rules() -> tuple[Rules, tuple[Order, Order]]:
    """The rules, and the lane's two rules in priority order: the order card's `when` and `then`, then its next rule."""
    o = load_with(FIXTURE)
    card = next(c for c in o.order_cards if c.store == "t_logs")
    assert card.tap_card is not None
    return to_rules(o), (Order(condition(card.when, set()), TapCard(CardId(card.tap_card))),
                         Order(AfterTime(0), TapCard(SWEEP)))


def completions(save: Save, rules: Rules, card: CardId) -> int:
    v = view(save, rules)
    return next((c.completions for c in (*v.cards, *v.completed) if c.card == card), 0)


def test_the_order_lands_all_three_stages_and_leaves_the_lane_on_its_next_rule():
    rules, orders = lane_rules()
    s = decide(advance(new_save(rules), rules, 0), rules, 0, SetOrders(orders))
    seen: list[int] = []
    for t in range(0, 1000, 10):
        s = advance(s, rules, t)
        seen.append(completions(s, rules, RAISE))
    assert seen[-1] == 3 and sorted(set(seen)) == [0, 1, 2, 3]
    assert tapped_cards(s, rules) == (SWEEP,)


def test_without_the_order_the_build_is_not_run():
    rules, orders = lane_rules()
    s = decide(advance(new_save(rules), rules, 0), rules, 0, SetOrders(orders[1:]))
    assert completions(advance(s, rules, 1000), rules, RAISE) == 0


def test_an_order_card_tapping_a_card_on_another_lane_fails_the_loader(tmp_path: Path):
    with pytest.raises(ValueError, match="does not take t_logs"):
        load_with(edited(tmp_path, 'tap_card = "t_raise"', 'tap_card = "t_haul"'))
