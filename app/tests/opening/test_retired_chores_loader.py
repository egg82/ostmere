"""Retired chores as content (engine DESIGN.txt, "Retired chores", "Content"), on fixtures/chores.toml merged onto the
opening alone: the next turn retires the clearing card's orders, and the loader refuses retire_orders anywhere but a
season's turn and on a card that cures no chore. Each refusal is the fixture edited, beside the control that loads."""
from pathlib import Path

import pytest

from ashfall_app.engine import AfterTime, CardId, Order, SetOrders, TapCard, advance, decide, new_save
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "chores.toml"
RETIRE = 'retire_orders = ["t_clear"]'
TURN_2 = 'id = "t_turn_2"\nseason = true\n'

PLANTS = (
    ("a card that cures no chore", "trigger t_turn_2: retires the orders on t_other, which cures no chip",
     ((RETIRE, 'retire_orders = ["t_other"]'),)),
    ("a card the heap's other maker makes", "trigger t_turn_2: retires the orders on t_clear, which cures no chip",
     (('makes = [{ store = "dry_wood", items_per_hour = 30 }]', 'makes = [{ store = "t_heap", items_per_hour = 30 }]'),)),
    ("an unknown card", "trigger t_turn_2: unknown card t_nope", ((RETIRE, 'retire_orders = ["t_nope"]'),)),
    ("a trigger that is not a season's turn", "trigger t_turn_2: retires orders but is not a season's turn",
     ((TURN_2, 'id = "t_turn_2"\n'),)),
    ("a trigger with no season", "trigger t_open: retires orders but is not a season's turn",
     ((f", {RETIRE} }}", " }"), ('{ unlock_kind = "card", id = "t_other" }] }', '{ unlock_kind = "card", id = "t_other" }], '
                                  + RETIRE + " }"))),
)


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def test_the_next_turn_removes_the_clearing_rule_and_keeps_the_rest():
    r = to_rules(load_with(FIXTURE))
    clear, other = Order(AfterTime(0), TapCard(CardId("t_clear"))), Order(AfterTime(0), TapCard(CardId("t_other")))
    s = decide(advance(new_save(r), r, 40_000), r, 40_000, SetOrders((clear, other)))
    assert advance(s, r, 50_399).orders == (clear, other)
    assert advance(s, r, 50_400).orders == (other,)


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p[0])
def test_each_plant_is_refused_with_its_message(tmp_path: Path, plant: tuple[str, str, tuple[tuple[str, str], ...]]):
    _, message, edits = plant
    with pytest.raises(ValueError) as caught:
        load_with(edited(tmp_path, *edits))
    assert str(caught.value).startswith(message)


def test_retire_orders_on_a_card_outcome_is_refused(tmp_path: Path):
    path = edited(tmp_path, (f", {RETIRE} }}", " }"), ('work_s = 60\ncosts', 'work_s = 60\ncap = 1\n'
                                                       f'outcome = {{ {RETIRE} }}\ncosts'))
    with pytest.raises(ValueError, match="^card t_clear: retires orders outside a season's turn"):
        load_with(path)
