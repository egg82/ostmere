"""A person's name slot (api/CONTRACT.txt, "Text and numbers", {<lane>}): a lane's name_key is a text key, served on
its LaneInfo, and a text's slot naming a lane must name one with a name_key; a digit in a slot's name is not a number."""
import pytest

from ashfall_app.api.service import Game
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def everything() -> Opening:
    """Every chapter, those in writing too, loaded once for the module: each chapter adds to the load."""
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def with_text(o: Opening, **text: str) -> Opening:
    return o.model_copy(update={"text": {**o.text, **text}})


def test_every_person_who_joins_has_a_name_and_their_named_label_is_it(everything: Opening):
    o = everything
    named = {x.id: x for x in o.lanes if x.name_key is not None}
    assert set(named) == {"n2", "n3", "n4", "n5", "n6", "n7"}
    for lane in named.values():
        assert lane.name_key is not None and o.text[lane.name_key]
        assert o.text[lane.later_labels[-1].label_key] == "{%s}" % lane.id


def test_the_content_serves_each_lanes_name_key(shipped_opening: Opening):
    o = shipped_opening
    infos = {x.lane: x.name_key for x in Game(o, ruleset(o, [], "test", 1)).content().lane_infos}
    assert infos["n2"] == "name_n2" and infos["hands"] is None and infos["n1"] is None


def test_a_slot_naming_a_named_lane_passes_and_holds_no_digit(everything: Opening):
    """Control: the checks pass a line that names a named person, so the failures below are the rule's doing."""
    check_opening(with_text(everything, l_his_watch="{n2} sits with {n3} and {n4}."))


def test_a_slot_naming_a_lane_with_no_name_fails(everything: Opening):
    with pytest.raises(ValueError, match="names lane n1, which has no name_key"):
        check_opening(with_text(everything, l_his_watch="{n1} sits down."))


def test_a_digit_outside_a_slot_still_fails(everything: Opening):
    with pytest.raises(ValueError, match="holds a digit"):
        check_opening(with_text(everything, l_his_watch="{n2} sits down 2 times."))


def test_a_name_key_missing_from_text_fails(everything: Opening):
    o = everything
    text = {k: v for k, v in o.text.items() if k != "name_n2"}
    with pytest.raises(ValueError, match="'name_n2' is not in text"):
        check_opening(o.model_copy(update={"text": text}))
