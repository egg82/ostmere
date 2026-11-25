"""The world map's places (api/CONTRACT.txt, "MAP", acceptance 1 to 3), on fixtures/places.toml merged onto the opening
alone. Each refusal is the fixture edited to break it, beside the unedited control that loads."""
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ashfall_app.api.map_models import PlaceInfo, Stamp
from ashfall_app.api.models import Unlock, UnlockKind
from ashfall_app.api.service import Game
from ashfall_app.main import create_app
from ashfall_app.opening.schema import OPENING, load_opening
from ashfall_app.saves.ruleset import ruleset
from tests.shipped_ruleset import ShippedRuleset

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "places.toml"
TEXT = FIXTURE.read_text()
HAMLET_AT = "at = [2, -1]"
WOODS_REVEAL = 'reveal = { unlock_kind = "card", id = "m_scout" }'


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = TEXT
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def game_of(*chapters: Path) -> Game:
    o = load_opening(OPENING, chapters)
    return Game(o, replace(ruleset(o, "test", 1)))


def later(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "later.toml"
    path.write_text(f"version = 1\n{body}")
    return path


# ---------- 1: the fixture loads and is served ----------

def test_the_fixture_is_served_in_content_order_with_each_field():
    places = game_of(FIXTURE).content().places
    assert places == [
        PlaceInfo(place="m_hamlet", stamp=Stamp.VILLAGE, east=2, north=-1, reveal=Unlock(category=UnlockKind.FEATURE, id="m_road"),
                  label_key="m_p_hamlet"),
        PlaceInfo(place="m_woods", stamp=Stamp.FOREST, east=-3, north=4, reveal=Unlock(category=UnlockKind.CARD, id="m_scout"),
                  label_key=None),
    ]


# ---------- 2: planted, each fails the load naming the place ----------

PLANTS = {
    "no reveal": ((WOODS_REVEAL + "\n", ""),),
    "a stamp outside the set": (('stamp = "forest"', 'stamp = "volcano"'),),
    "a reveal of kind offer": ((WOODS_REVEAL, 'reveal = { unlock_kind = "offer", id = "m_scout" }'),),
    "a reveal of an unknown feature": ((WOODS_REVEAL, 'reveal = { unlock_kind = "feature", id = "m_nowhere" }'),),
    "a reveal nothing unlocks": ((WOODS_REVEAL, 'reveal = { unlock_kind = "feature", id = "m_never" }'),
                                 ('[[features]]\nid = "m_road"\n', '[[features]]\nid = "m_road"\n\n[[features]]\nid = "m_never"\n')),
    "two places on one cell": (("at = [-3, 4]", HAMLET_AT),),
    "a place on the town's cell": (("at = [-3, 4]", "at = [0, 0]"),),
    "an at past the reach": (("at = [-3, 4]", "at = [-3, 9]"),),
    "a label_key not in text": ((WOODS_REVEAL, WOODS_REVEAL + '\nlabel_key = "m_p_unwritten"'),),
}
NAMED = {"no reveal": "reveal", "a stamp outside the set": "stamp"}


@pytest.mark.parametrize("plant", PLANTS)
def test_each_plant_fails_the_load_naming_the_place(tmp_path: Path, plant: str):
    with pytest.raises(ValueError) as e:
        load_opening(OPENING, (edited(tmp_path, *PLANTS[plant]),))
    assert NAMED.get(plant, "place m_woods") in str(e.value), str(e.value)


def test_two_places_on_one_cell_across_two_chapters_fail_naming_both(tmp_path: Path):
    second = later(tmp_path, '[[places]]\nid = "m_ford"\nstamp = "crossing"\n' + HAMLET_AT
                   + '\nreveal = { unlock_kind = "feature", id = "m_road" }\n')
    with pytest.raises(ValueError) as e:
        load_opening(OPENING, (FIXTURE, second))
    assert "place m_ford" in str(e.value) and "place m_hamlet" in str(e.value), str(e.value)


def test_a_reveal_by_a_journal_entry_loads(tmp_path: Path):
    second = later(tmp_path, '[[entries]]\nid = "m_page"\nsection = "places"\nhand = "ink"\nrunners = []\n'
                   '[[notes]]\nid = "m_page_note"\nentry = "m_page"\ngate = { test = "after_time", value = 5 }\n'
                   '[[places]]\nid = "m_ford"\nstamp = "crossing"\nat = [1, 1]\nreveal = { unlock_kind = "entry", id = "m_page" }\n'
                   '[text]\nm_page_note = "A ford."\n')
    assert [p.id for p in load_opening(OPENING, (FIXTURE, second)).places] == ["m_hamlet", "m_woods", "m_ford"]


# ---------- 3: the shipped content's places ----------

def test_the_shipped_content_serves_its_places_in_content_order(shipped_ruleset: ShippedRuleset):
    places = shipped_ruleset.make_game(shipped_ruleset.opening, shipped_ruleset.rs).content().places
    assert [(p.place, p.stamp, p.reveal.id, p.label_key) for p in places] == [
        ("p_ridge", Stamp.MOUNTAIN, "r2_open", "place_ridge"), ("p_far_hills", Stamp.RANGE, "r2_open", None),
        ("p_ashwood", Stamp.FOREST, "ashwood", "place_ashwood"), ("p_square_hill", Stamp.HILL_VILLAGE, "square_hill_seen", None),
        ("p_warm_patch", Stamp.FORT, "post_shown", "place_warm_patch")]


def test_the_spec_names_the_maps_components():
    schemas: dict[str, Any] = create_app().openapi()["components"]["schemas"]
    assert {"PlaceInfo", "Stamp"} <= set(schemas)
    assert schemas["Content"]["properties"]["places"]["items"] == {"$ref": "#/components/schemas/PlaceInfo"}
