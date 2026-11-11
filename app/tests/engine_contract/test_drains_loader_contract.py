"""Drains, part six: the loader's fractions and drains (engine DESIGN.txt, "FRACTIONS AT THE LOADER", invariant 132).
Written blind from that part, the entry types (opening/entries.py) and the loader's public functions; the `kills`
marker names the rows of MUTANTS_drains.txt each test must turn red for.

fixtures/drains_chapter.toml is merged onto the opening alone; its @SLOTS@ are filled here, each default the plain shape
that loads, so a refusal is one slot edited beside a control that loads."""
import re
from pathlib import Path

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, RATE_SCALE, Amount, AtLeast, AtMost, CardDef, Flow, InvalidRulesError, Rules, StoreId,
    StoreValue, per_hour,
)
from ashfall_app.opening.schema import OPENING, load_opening, to_rules
from drains_world import kills

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "drains_chapter.toml"
WHEN = '{ test = "at_most", subject_kind = "store", id = "t_x", value = 3, release = 6 }'
DEFAULTS = {
    "SRC_MAKE": "items_per_hour = 2", "SRC_COST": "items_per_hour = 1", "CARD_MAKE": "items_per_hour = 3",
    "CARD_COST": "items_per_hour = 6", "DRAIN": '{ store = "t_x", items = 3 }', "CHIP_WHEN": WHEN,
    "COLD_CHIP_WHEN": '{ test = "at_most", subject_kind = "store", id = "t_heat", value = 3, release = 6 }',
    "ORDER_WHEN": '{ test = "at_most", subject_kind = "store", id = "t_heat", value = 3, release = 6 }',
    "TRIGGER_WHEN": '{ test = "at_least", subject_kind = "store", id = "t_x", value = 1 }', "FLOWS_EXTRA": "",
}


def render(tmp_path: Path, **slots: str) -> Path:
    unknown = set(slots) - set(DEFAULTS)
    assert not unknown, unknown
    text = FIXTURE.read_text()
    for name, default in DEFAULTS.items():
        text = text.replace(f"@{name}@", slots.get(name, default))
    assert not re.search(r"@[A-Z_]+@", text)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def rules(tmp_path: Path, **slots: str) -> Rules:
    return to_rules(load_opening(OPENING, (render(tmp_path, **slots),)))


def card(r: Rules, id_: str) -> CardDef:
    return next(c for c in r.cards if c.id == id_)


def refused(tmp_path: Path, entry: str, **slots: str) -> None:
    with pytest.raises(ValueError, match=entry):
        rules(tmp_path, **slots)


def test_the_plain_fixture_loads_with_every_at_one_as_the_loader_always_did(tmp_path: Path):
    r = rules(tmp_path)
    flows = card(r, "t_flows")
    assert (flows.makes[0], flows.costs[0]) == (Flow(StoreId("t_y"), per_hour(3)), Flow(StoreId("t_x"), per_hour(6)))
    assert card(r, "t_cure").drains == (Amount(StoreId("t_x"), 3 * Q),)
    assert next(c for c in r.chips if c.id == "t_warm").when == AtMost(StoreValue(StoreId("t_x")), 3 * Q, 6 * Q)


# ---- every_hours (22, 19) ------------------------------------------------------------------------------------

@kills(22)
@pytest.mark.parametrize("items,hours", [(3, 2), (1, 8), (6, 4), (5, 5), (7, 1)])
def test_every_hours_k_gives_items_per_hour_over_k_for_every_flow_of_a_card_and_a_standing_action(
        tmp_path: Path, items: int, hours: int):
    """Invariant 132: per_hour == items_per_hour * RATE_SCALE / k, on makes and costs, card and standing alike."""
    shape = f"items_per_hour = {items}, every_hours = {hours}"
    r = rules(tmp_path, CARD_MAKE=shape, CARD_COST=shape, SRC_MAKE=shape, SRC_COST=shape)
    expected = items * RATE_SCALE // hours
    assert items * RATE_SCALE % hours == 0
    flows = card(r, "t_flows")
    src = next(a for a in r.standing if a.id == "t_src")
    assert (flows.makes[0].per_hour, flows.costs[0].per_hour) == (expected, expected)
    assert (src.makes[0].per_hour, src.costs[0].per_hour) == (expected, expected)


@kills(22)
def test_every_hours_leaves_xp_and_the_camps_make_flow_alone(tmp_path: Path):
    """Invariant 132: only a card's and a standing action's makes and costs divide; xp_per_hour does not, and the camp's
    flow (added to every hands card) is the camp's own rate on a card whose flows are divided as on any other."""
    opening = load_opening(OPENING, ())
    assert opening.camp is not None
    camp = StoreId(opening.camp.store)
    plain = rules(tmp_path)
    divided = rules(tmp_path, CARD_MAKE="items_per_hour = 3, every_hours = 2", CARD_COST="items_per_hour = 6, every_hours = 3")
    for r in (plain, divided):
        flows = card(r, "t_flows")
        assert flows.xp_per_hour == per_hour(6)
        assert [f.per_hour for f in flows.makes if f.store == camp] == [per_hour(opening.camp.items_per_hour)]
        assert [f.per_hour for f in card(r, "t_cure").makes if f.store == camp] == [per_hour(opening.camp.items_per_hour)]


@kills(19)
@pytest.mark.parametrize("slot", ["CARD_MAKE", "CARD_COST", "SRC_MAKE", "SRC_COST"])
@pytest.mark.parametrize("items,hours", [(1, 7), (1, 3), (3, 7)])
def test_an_every_hours_that_does_not_divide_exactly_is_refused_not_rounded(
        tmp_path: Path, slot: str, items: int, hours: int):
    assert items * RATE_SCALE % hours != 0
    entry = "t_src" if slot.startswith("SRC") else "t_flows"
    refused(tmp_path, entry, **{slot: f"items_per_hour = {items}, every_hours = {hours}"})


# ---- drains in content (19, 23) -----------------------------------------------------------------------------------

@kills(19)
@pytest.mark.parametrize("items,every,quantity", [(3, 4, 2_700_000), (1, 2, 1_800_000), (5, 1, 18_000_000), (1, 36, 100_000)])
def test_a_drain_is_exact_as_an_input_is_items_per_every_completions(tmp_path: Path, items: int, every: int, quantity: int):
    assert items * Q % every == 0 and items * Q // every == quantity
    r = rules(tmp_path, DRAIN=f'{{ store = "t_x", items = {items}, every = {every} }}')
    assert card(r, "t_cure").drains == (Amount(StoreId("t_x"), quantity),)


@kills(19)
@pytest.mark.parametrize("every", [7, 11, 13])
def test_a_drain_that_does_not_divide_into_quantity_units_is_refused(tmp_path: Path, every: int):
    assert Q % every != 0
    refused(tmp_path, "t_cure", DRAIN=f'{{ store = "t_x", items = 1, every = {every} }}')


@kills(23)
def test_a_drain_on_a_tally_store_is_refused_and_on_a_plain_store_is_not(tmp_path: Path):
    rules(tmp_path, DRAIN='{ store = "t_y", items = 1 }')
    refused(tmp_path, "t_cure|t_tally", DRAIN='{ store = "t_tally", items = 1 }')


@kills(18)
def test_a_drain_the_engine_refuses_fails_to_rules_naming_the_card(tmp_path: Path):
    """Content's drains reach the engine's validation: a drain on a store the card also spends as a cost."""
    opening = load_opening(OPENING, (render(tmp_path, FLOWS_EXTRA='drains = [{ store = "t_x", items = 1 }]'),))
    with pytest.raises(InvalidRulesError, match="t_flows"):
        to_rules(opening)


# ---- ConditionEntry.every (20, 21) -------------------------------------------------------------------------------

def chip_when(r: Rules) -> AtMost | AtLeast:
    when = next(c for c in r.chips if c.id == "t_warm").when
    assert isinstance(when, (AtMost, AtLeast))
    return when


def cond(test: str, value: int, release: int | None = None, every: int | None = None, store: str = "t_x") -> str:
    parts = [f'test = "{test}"', 'subject_kind = "store"', f'id = "{store}"', f"value = {value}"]
    if release is not None:
        parts.append(f"release = {release}")
    if every is not None:
        parts.append(f"every = {every}")
    return "{ " + ", ".join(parts) + " }"


@kills(20)
@pytest.mark.parametrize("value,release,every,expected", [
    (3, 6, 2, (3 * Q // 2, 6 * Q // 2)), (3, None, 2, (3 * Q // 2, 3 * Q // 2)), (1, 4, 4, (Q // 4, Q)),
    (3, 6, 36, (3 * Q // 36, 6 * Q // 36)),
])
def test_every_divides_value_and_release_alike_on_a_store(
        tmp_path: Path, value: int, release: int | None, every: int, expected: tuple[int, int]):
    r = rules(tmp_path, CHIP_WHEN=cond("at_most", value, release, every))
    when = chip_when(r)
    assert isinstance(when, AtMost) and when.subject == StoreValue(StoreId("t_x"))
    assert (when.value, when.release) == expected


@kills(20)
def test_every_divides_an_at_least_condition_too(tmp_path: Path):
    r = rules(tmp_path, TRIGGER_WHEN=cond("at_least", 3, None, 2))
    when = next(t for t in r.triggers if t.id == "t_trig").when
    assert isinstance(when, AtLeast) and (when.value, when.release) == (3 * Q // 2, 3 * Q // 2)


@kills(19, 20)
@pytest.mark.parametrize("value,release,every", [(1, None, 7), (7, 8, 7), (3, 6, 7), (1, 2, 11)])
def test_an_every_that_does_not_divide_value_or_release_exactly_is_refused(
        tmp_path: Path, value: int, release: int | None, every: int):
    """Invariant 132: each of value and release is refused alone when inexact (7/7 is exact, 8/7 and 1/7 are not)."""
    assert (value * Q % every != 0) or (release is not None and release * Q % every != 0)
    refused(tmp_path, "t_warm", CHIP_WHEN=cond("at_most", value, release, every))


PLAIN = {
    "after_time": '{ test = "after_time", value = 10 }',
    "a skill level": '{ test = "at_least", subject_kind = "skill_level", id = "t_k", value = 2 }',
    "a card count": '{ test = "at_least", subject_kind = "card_count", id = "t_cure", value = 2 }',
    "an unlock": '{ test = "at_least", subject_kind = "unlocked", unlock_kind = "card", id = "t_cure", value = 1 }',
    "a running card": '{ test = "at_least", subject_kind = "running", id = "t_cure", value = 1 }',
    "a lane's rules": '{ test = "at_least", subject_kind = "lane_rules", id = "t_helper", value = 1 }',
}


@kills(21)
@pytest.mark.parametrize("when", PLAIN.values(), ids=PLAIN.keys())
def test_every_is_refused_on_any_subject_but_a_store(tmp_path: Path, when: str):
    rules(tmp_path, TRIGGER_WHEN=when)
    refused(tmp_path, "t_trig", TRIGGER_WHEN=when[:-2] + ", every = 2 }")


@kills(21)
def test_every_is_refused_on_an_order_cards_when_and_not_on_its_chip_alone(tmp_path: Path):
    """A rule's levels are worded in whole items, so a chip whose `when` has `every` has no order card; the chip alone
    (t_warm has none) takes it."""
    rules(tmp_path, CHIP_WHEN=cond("at_most", 3, 6, 2))
    half = cond("at_most", 3, 6, 2, "t_heat")
    refused(tmp_path, "t_cold|t_heat|t_stoke", COLD_CHIP_WHEN=half, ORDER_WHEN=half)


@kills(21)
def test_every_at_one_is_the_loader_before_this_part(tmp_path: Path):
    """Invariant 132: an explicit every = 1 and every_hours = 1 load as the written whole items."""
    a = rules(tmp_path, CHIP_WHEN=cond("at_most", 3, 6), CARD_MAKE="items_per_hour = 3")
    b = rules(tmp_path, CHIP_WHEN=cond("at_most", 3, 6, every=1), CARD_MAKE="items_per_hour = 3, every_hours = 1")
    assert a == b
