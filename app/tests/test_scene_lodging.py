"""Where each person sleeps (`lodging` on a lane, lane_entries.LodgingEntry) and the scene that shows the hall lived in
(tools/scene/people_hall.py): every person's lane says, a `build` names a card, and the scene retires at night only the
idle poses of people the content lodges in that build."""
import sys
from pathlib import Path

import pytest

from ashfall_app.opening.lane_entries import LaneEntry, LodgingEntry
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import people_hall   # tools/scene, on the path from the line above


def person_lanes(o: Opening) -> list[LaneEntry]:
    return [x for x in o.lanes if x.ruled and not x.station and not x.pooled]


def unlodged(o: Opening) -> list[str]:
    return [x.id for x in person_lanes(o) if x.lodging is None]


def bad_builds(o: Opening) -> list[str]:
    cards = {c.id for c in o.cards}
    return [f"{x.id}: {x.lodging.build}" for x in person_lanes(o)
            if x.lodging is not None and x.lodging.build is not None and x.lodging.build not in cards]


def retired_but_not_lodged(o: Opening, table: dict[str, tuple[str, ...]]) -> list[str]:
    """People the scene sends home at night whom the content does not lodge in the hall."""
    in_hall = {x.id for x in person_lanes(o) if x.lodging is not None and x.lodging.build == "hall"}
    return sorted(set(table) - in_hall)


@pytest.fixture(scope="module")
def content() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def test_every_person_says_where_they_sleep(content: Opening):
    assert len(person_lanes(content)) > 10, "almost no people seen: the check is blind"
    assert unlodged(content) == []


def test_a_lodging_names_a_card(content: Opening):
    assert any(x.lodging is not None and x.lodging.build for x in content.lanes), "no lodging names a build"
    assert bad_builds(content) == []


def test_the_scene_sends_home_only_people_the_hall_lodges(content: Opening):
    assert retired_but_not_lodged(content, people_hall.IDLE) == []
    assert retired_but_not_lodged(content, {**people_hall.IDLE, "n13": ("figure_n13_outside_ring",)}) == ["n13"]


def test_the_idle_poses_it_retires_are_scene_layers():
    import json
    layers = set(json.loads((SCENE / "shown.json").read_text())["layers"])
    assert [i for ids in people_hall.IDLE.values() for i in ids if i not in layers] == []


def test_a_lodging_needs_exactly_one_answer():
    LodgingEntry.model_validate({"build": "hall"})
    for fields in ({}, {"build": "hall", "elsewhere": "x"}):
        with pytest.raises(ValueError, match="exactly one of build and elsewhere"):
            LodgingEntry.model_validate(fields)
