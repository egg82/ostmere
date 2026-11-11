"""A chip's cost, as a contract (api/CONTRACT.txt). Written blind: a chip has a cost_key exactly when it has effects;
a chip with effects and an offered_after fails the load; ChipInfo.cost_key is a nullable string; the shipped opening's
cold, hungry and tired chips carry the stated effects."""
from typing import Any

import pytest

from ashfall_app.api.content_models import ChipInfo
from ashfall_app.engine import HANDS, ActionId, FlowKind, LaneSpeed, Modifier, ModifierKind, RateRef, SourceId, StoreId
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.schema import Opening, load_opening, to_rules

SHIPPED = load_opening()


def chip_dicts() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """The shipped opening as plain data, and its chips within it."""
    data: dict[str, Any] = SHIPPED.model_dump(mode="json")
    chips: list[dict[str, Any]] = data["chips"]
    return data, chips


def load_with(chip_id: str, **changes: Any) -> None:
    """The shipped opening with one chip's fields replaced (a key set to None is removed), through the model's own
    validation and the opening's checks: what loading the file does after parsing it."""
    data, chips = chip_dicts()
    chip = next(c for c in chips if c["id"] == chip_id)
    for key, value in changes.items():
        if value is None:
            chip.pop(key, None)
        else:
            chip[key] = value
    check_opening(Opening.model_validate(data))


def a_chip_with_effects() -> dict[str, Any]:
    _, chips = chip_dicts()
    return next(c for c in chips if c.get("effects") and c.get("cost_key"))


def test_the_control_an_unchanged_chip_loads():
    """The harness can pass: round-tripping the shipped opening through the same path loads, so the failures below are
    the rule's doing."""
    data, _ = chip_dicts()
    check_opening(Opening.model_validate(data))


def test_the_shipped_chips_have_a_cost_key_exactly_when_they_have_effects():
    chips = to_rules(SHIPPED).chips
    entries = {c.id: c for c in SHIPPED.chips}
    assert any(c.effects for c in chips)
    for chip in chips:
        assert (entries[chip.id].cost_key is not None) == bool(chip.effects), chip.id


def test_a_chip_with_effects_and_no_cost_key_fails_the_load():
    with pytest.raises(ValueError):
        load_with(a_chip_with_effects()["id"], cost_key=None)


def test_a_chip_with_a_cost_key_and_no_effects_fails_the_load():
    with pytest.raises(ValueError):
        load_with(a_chip_with_effects()["id"], effects=[])


def test_a_chip_with_effects_and_an_offered_after_fails_the_load():
    chip = a_chip_with_effects()
    with pytest.raises(ValueError):
        load_with(chip["id"], offered_after={"unlock_kind": "action", "id": "fire"})


def test_a_chip_without_effects_may_have_an_offered_after():
    """The control for the rule above: with its effects and cost removed, the same chip takes the offered_after."""
    load_with(a_chip_with_effects()["id"], effects=[], cost_key=None, offered_after={"unlock_kind": "action", "id": "fire"})


def test_chipinfo_cost_key_is_a_nullable_string():
    schema = ChipInfo.model_json_schema()
    assert "cost_key" in schema["required"]
    kinds = sorted(branch["type"] for branch in schema["properties"]["cost_key"]["anyOf"])
    assert kinds == ["null", "string"]


HANDS_LANE = LaneSpeed(HANDS)
COSTS = {
    "cold": Modifier(HANDS_LANE, ModifierKind.MUL_BP, 8_000, SourceId("cold")),
    "hungry": Modifier(RateRef(ActionId("weariness"), FlowKind.COST, StoreId("energy")), ModifierKind.MUL_BP, 15_000, SourceId("hungry")),
    "tired": Modifier(HANDS_LANE, ModifierKind.MUL_BP, 5_000, SourceId("tired")),
}


@pytest.mark.parametrize("chip_id", sorted(COSTS))
def test_the_shipped_chips_carry_the_stated_costs(chip_id: str):
    chip = next(c for c in to_rules(SHIPPED).chips if c.id == chip_id)
    assert COSTS[chip_id] in chip.effects, chip.effects
