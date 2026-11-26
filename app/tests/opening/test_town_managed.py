"""What the Town view asks the player to tune, reported per chapter end (tests/opening/town_readout.py) and never refused:
how many is a feel (docs/decisions/people.md, "The mark: who keeps their own split"). What is refused is structure: a group
holding work a member cannot do (opening/groups.py, check_group_abilities). On the shipped chapters, with planted changes."""
import pytest

from ashfall_app.opening.groups import check_groups
from ashfall_app.opening.schema import Opening
from tests import readout_snapshot as rs
from tests.opening import town_readout
from tests.opening.town_readout import town_managed


def without_marks(o: Opening, *triggers: str) -> Opening:
    assert set(triggers) <= {t.id for t in o.triggers}, triggers
    return o.model_copy(update={"triggers": [t.model_copy(update={"outcome": t.outcome.model_copy(update={"marks": []})})
                                             if t.id in triggers else t for t in o.triggers]})


def on_lanes(o: Opening, card: str, *lanes: str) -> Opening:
    """`o` with the town card `card` also fanned out to `lanes`."""
    assert card in {tc.id for tc in o.town_cards}, card
    return o.model_copy(update={"town_cards": [tc.model_copy(update={"lanes": [*tc.lanes, *lanes]}) if tc.id == card else tc
                                               for tc in o.town_cards]})


def test_the_committed_readouts_are_the_ones_the_town_writes():
    assert rs.stray("town", town_readout.NAMES) == ([], [])


def test_the_town_readout_is_reported():
    text = town_readout.readouts()["town"]
    assert len(text.splitlines()) == len(town_readout.CHAPTERS) + 1
    rs.check("town", text)


def test_the_shipped_town_keeps_its_notables_and_hands_the_rest_to_groups(shipped_opening: Opening):
    own, groups = town_managed(shipped_opening)
    assert own == ["n1", "n2", "n3", "n4", "n13", "n23"]
    assert set(groups) == {"g_field", "g_road"}
    assert "n11" not in groups["g_field"]


@pytest.mark.parametrize(("withheld", "named"), [
    (("t_family_groups",), ["n5", "n6", "n7"]),
    (("t_choir_groups_beds", "t_choir_groups_road"), ["n8", "n9", "n10"]),
    (("t_cutter_groups_beds", "t_cutter_groups_road"), ["n12"]),
], ids=["day eleven's family", "day eighteen's three", "day eighteen's sister"])
def test_a_newcomer_left_with_a_bar_is_reported_as_a_person_and_nothing_fails(shipped_opening: Opening,
                                                                              withheld: tuple[str, ...], named: list[str]):
    planted = without_marks(shipped_opening, *withheld)
    check_groups(planted)
    own, groups = town_managed(planted)
    assert all(lane in own and all(lane not in m for m in groups.values()) for lane in named)


def test_a_group_holds_only_work_each_member_with_a_list_can_do(shipped_opening: Opening):
    check_groups(shipped_opening)
    with pytest.raises(ValueError, match=r"town card \{lane\}_fog_fish: is on group g_field, and its members n11 cannot do it"):
        check_groups(on_lanes(shipped_opening, "{lane}_fog_fish", "g_field"))


def test_a_member_with_no_list_of_their_own_takes_the_groups(shipped_opening: Opening):
    listless = {x.id for x in shipped_opening.lanes if x.group == "g_road"} - {ln for tc in shipped_opening.town_cards
                                                                              for ln in tc.lanes}
    assert listless
    check_groups(on_lanes(shipped_opening, "{lane}_clear_roofs", "g_road", *sorted(
        {x.id for x in shipped_opening.lanes if x.group == "g_road"} - listless)))
