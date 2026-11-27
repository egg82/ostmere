"""Where each person stands by day (`by_day` on a lane, lane_entries.ByDayEntry) and the scene that draws it (tools/scene/cast/people_day.py):
a `card` names a card of the person's own lane (or of their crew's) whose `site` is a scene layer, `at_fire` the reason the content seats them at the
camp fire, `off_scene` why their work or place is outside what the scene draws. The scene moves only the people the content sends to a site, to that card's layer; the lanes with no `by_day` are held
(`people_day.HELD_UNDECIDED`, only shrinks)."""
import json
import sys
from pathlib import Path

import pytest

from ashfall_app.rules.entries.lane_entries import ByDayEntry
from ashfall_app.rules.schema import CHAPTERS, IN_WRITING, Opening, load_opening
from tests.test_scene_lodging import person_lanes

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
from cast import people_day   # tools/scene, on the path from the line above


def undecided(o: Opening) -> set[str]:
    return {x.id for x in person_lanes(o) if x.by_day is None}


def bad_cards(o: Opening) -> list[str]:
    """`by_day` cards that are not a card of the lane's own or its crew's, or whose site is not a layer."""
    cards = {c.id: c for c in o.cards}
    out: list[str] = []
    for x in person_lanes(o):
        if x.by_day is None or x.by_day.card is None:
            continue
        c = cards.get(x.by_day.card)
        if c is None or c.lane not in (x.id, x.group) or c.site is None or c.site.layer is None:
            out.append(f"{x.id}: {x.by_day.card}")
    return out


def sited_layers(o: Opening) -> dict[str, str]:
    """Each person the content sends to a card's site, to the layer that site names."""
    cards = {c.id: c for c in o.cards}
    out: dict[str, str] = {}
    for x in person_lanes(o):
        site = cards[x.by_day.card].site if x.by_day is not None and x.by_day.card is not None else None
        if site is not None and site.layer is not None:
            out[x.id] = site.layer
    return out


def scene_disagrees(o: Opening, table: dict[str, "people_day.Work"]) -> list[str]:
    want = sited_layers(o)
    return sorted([f"{p}: scene has none" for p in want.keys() - table.keys()]
                  + [f"{p}: content does not send them to a site" for p in table.keys() - want.keys()]
                  + [f"{p}: scene {table[p].layer}, content {want[p]}" for p in table.keys() & want.keys()
                     if table[p].layer != want[p]])


@pytest.fixture(scope="module")
def content() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def test_a_lane_without_by_day_is_held_and_only_it(content: Opening):
    assert len(person_lanes(content)) > 10, "almost no people seen: the check is blind"
    assert undecided(content) == set(people_day.HELD_UNDECIDED), "a lane gained a `by_day`, or lost its one: lower or fix the held set"
    stripped = content.model_copy(update={"lanes": [x.model_copy(update={"by_day": None}) if x.id == "n11" else x for x in content.lanes]})
    assert undecided(stripped) == {"n11"} != set(people_day.HELD_UNDECIDED), "the check cannot see a lane with no answer"


def test_a_by_day_card_is_the_lanes_or_its_crews_and_sited(content: Opening):
    assert any(x.by_day is not None and x.by_day.card for x in content.lanes), "no `by_day` names a card"
    assert bad_cards(content) == []
    other = content.model_copy(update={"lanes": [x.model_copy(update={"by_day": ByDayEntry(card="n3_sow")}) if x.id == "n2" else x
                                                 for x in content.lanes]})
    assert bad_cards(other) == ["n2: n3_sow"], "the check cannot see another lane's card"


def test_the_scene_stands_people_at_the_site_the_content_names(content: Opening):
    assert scene_disagrees(content, people_day.AT_WORK) == []
    assert scene_disagrees(content, {}) != [], "the check cannot see a missing pose"
    wrong = {**people_day.AT_WORK, "n3": people_day.AT_WORK["n3"]._replace(layer="fire_lit")}
    assert scene_disagrees(content, wrong) == ["n3: scene fire_lit, content beds_3"]
    assert scene_disagrees(content, {**people_day.AT_WORK, "n4": people_day.AT_WORK["n3"]}) == ["n4: content does not send them to a site"]


def test_the_scene_layers_it_names_exist():
    layers = set(json.loads((SCENE / "audits" / "shown.json").read_text())["layers"])
    names = [i for w in people_day.AT_WORK.values() for i in (w.layer, w.by_fire or w.crew)]
    names += [people_day.layer_id(p) for p in people_day.AT_WORK]
    assert [i for i in names if i not in layers] == []


def test_a_by_day_needs_exactly_one_answer():
    for ok in ({"card": "x"}, {"at_fire": "x"}, {"off_scene": "x"}):
        ByDayEntry.model_validate(ok)
    for fields in ({}, {"card": "x", "at_fire": "y"}, {"at_fire": "x", "off_scene": "y"}):
        with pytest.raises(ValueError, match="exactly one of card, at_fire and off_scene"):
            ByDayEntry.model_validate(fields)
