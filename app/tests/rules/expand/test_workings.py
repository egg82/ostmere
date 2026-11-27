"""Workings as data (ashfall_app/rules/expand/workings.py): a chapter's `[[workings]]` entry expands to one ordinary card,
its tithe a pure function of the axes read from working_rules.toml."""
from pathlib import Path

import pytest

from ashfall_app.rules.chapters import merge
from ashfall_app.rules.entries.entries import CardEntry, ItemAmount, OutcomeEntry
from ashfall_app.rules.schema import CHAPTERS, OPENING, Chapter, Opening, load_opening
from ashfall_app.rules.expand.workings import WorkingEntry, load_rules, tithe
from tests.rules.play.playthrough import opening

SPEC = {
    "id": "fixture_working", "label_key": "c_warm_beds", "upside_key": "up_warm_beds", "work_s": 600,
    "skill": "spellcraft", "xp_per_hour": 120, "input": {"store": "rime", "items": 3},
    "from_kind": "heat", "to_kind": "light", "distance": 2, "link": "none",
}
TOML = """version = 1

[[workings]]
id = "fixture_working"
label_key = "c_warm_beds"
upside_key = "up_warm_beds"
work_s = 600
skill = "spellcraft"
xp_per_hour = 120
from_kind = "heat"
to_kind = "light"
distance = 2
link = "none"
"""


def computed(**axes: object) -> int:
    spec = {**SPEC, **axes}
    return tithe(load_rules(), str(spec["from_kind"]), str(spec["to_kind"]), int(str(spec["distance"])), str(spec["link"]))


def expanded(o: Opening, **fields: object) -> CardEntry:
    ch = Chapter.model_validate({"version": 1, "workings": [{**SPEC, **fields}]})
    return next(c for c in merge(o, ch).cards if c.id == SPEC["id"])


def test_a_fixture_working_expands_to_the_expected_card():
    card = expanded(opening())
    assert card == CardEntry(
        id="fixture_working", lane="hands", only_player="magic", presentation="action", label_key="c_warm_beds",
        upside_key="up_warm_beds", work_s=600, skill="spellcraft", xp_per_hour=120,
        inputs=[ItemAmount(store="rime", items=3)], outcome=OutcomeEntry(stores=[ItemAmount(store="ash", items=4)]),
    )


@pytest.mark.parametrize(("axis", "other"), [("distance", 3), ("to_kind", "heat"), ("link", "material")])
def test_changing_one_axis_changes_the_cost_by_the_tables_step(axis: str, other: object):
    rules = load_rules()
    kind = {(k.from_, k.to): k.tithe for k in rules.kinds}
    steps = {"distance": rules.distance_step, "to_kind": kind["heat", "heat"] - kind["heat", "light"],
             "link": -next(x.discount for x in rules.links if x.id == "material")}
    assert steps[axis] != 0
    base = computed()
    changed = computed(**{axis: other})
    assert changed - base == steps[axis]
    assert expanded(opening(), **{axis: other}).outcome.stores[0].items == changed


def test_a_declared_tithe_that_matches_is_accepted():
    assert expanded(opening(), tithe=computed()).outcome.stores[0].items == computed()


def test_a_declared_tithe_that_differs_is_refused_naming_the_id(tmp_path: Path):
    path = tmp_path / "planted.toml"
    path.write_text(TOML + f"tithe = {computed() + 1}\n")
    with pytest.raises(ValueError, match="working fixture_working: declares a tithe of 5, the rules compute 4"):
        load_opening(OPENING, (*CHAPTERS, path))


def test_the_unplanted_fixture_loads_through_the_loader(tmp_path: Path):
    """The control for the refusal above: the same entry without the declared tithe loads, so the refusal is the tithe's."""
    path = tmp_path / "fixture.toml"
    path.write_text(TOML)
    card = next(c for c in load_opening(OPENING, (*CHAPTERS, path)).cards if c.id == "fixture_working")
    assert card.outcome.stores[0].items == 4


def test_an_axis_the_table_has_no_row_for_is_refused():
    with pytest.raises(ValueError, match="no tithe rule for moving heat into sense"):
        expanded(opening(), to_kind="sense")
    with pytest.raises(ValueError, match="no tithe rule for the link 'wish'"):
        expanded(opening(), link="wish")


# The two shipped working cards (released, so left as cards), written as the rows that would compute them.
SHIPPED = [
    {"id": "warm_beds", "label_key": "c_warm_beds", "upside_key": "up_warm_beds", "work_s": 900, "skill": "spellcraft",
     "xp_per_hour": 360, "input": {"store": "rime", "items": 6}, "from_kind": "heat", "to_kind": "heat", "distance": 1},
    {"id": "stir_air", "label_key": "c_stir_air", "upside_key": "up_wash_meat", "work_s": 900, "skill": "spellcraft",
     "xp_per_hour": 360, "input": {"store": "film", "items": 12}, "from_kind": "motion", "to_kind": "motion",
     "distance": 2, "link": "material"},
]


@pytest.mark.parametrize("row", SHIPPED, ids=[str(r["id"]) for r in SHIPPED])
def test_the_computed_row_of_a_shipped_working_matches_its_card(row: dict[str, object]):
    shipped = next(c for c in opening().cards if c.id == row["id"])
    made = WorkingEntry.model_validate(row).card(load_rules())
    ash = [s for s in shipped.outcome.stores if s.store == "ash"]
    assert made.outcome.stores == ash
    for field in ("only_player", "presentation", "label_key", "upside_key", "work_s", "skill", "xp_per_hour", "inputs"):
        assert getattr(made, field) == getattr(shipped, field), field
