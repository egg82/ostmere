"""What the Town view asks the player to tune, reported per chapter end (tests/opening/town_readout.py) and never refused:
how many is a feel (docs/decisions/people.md, "The mark: who keeps their own split"). What is refused is structure: a group
holding work a member cannot do (opening/groups.py, check_group_abilities). On the shipped chapters, with planted changes."""
import pytest

from ashfall_app.opening.groups import check_groups, with_crews
from ashfall_app.opening.lane_entries import LaneEntry
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
    assert own == ["n1", "n3", "n13", "n23"]
    assert set(groups) == {"g_field", "g_hearth", "g_road"}
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
    with pytest.raises(ValueError, match=r"town card \{lane\}_fog_fish: is on group g_hearth, and its members n11 cannot do it"):
        check_groups(on_lanes(shipped_opening, "{lane}_fog_fish", "g_hearth"))


def test_a_member_with_no_list_of_their_own_takes_the_groups(shipped_opening: Opening):
    listless = {x.id for x in shipped_opening.lanes if x.group == "g_road"} - {ln for tc in shipped_opening.town_cards
                                                                              for ln in tc.lanes}
    assert listless
    check_groups(on_lanes(shipped_opening, "{lane}_clear_roofs", "g_road", *sorted(
        {x.id for x in shipped_opening.lanes if x.group == "g_road"} - listless)))


PEOPLE = {f"n{i}" for i in range(2, 13)}


def lane(lane_id: str, *, crews: tuple[str, ...] = (), group: str | None = None, pooled: bool = False) -> LaneEntry:
    return LaneEntry(id=lane_id, label_key="x", ruled=True, pooled=pooled, crews=list(crews), group=group)


def test_a_person_goes_to_the_smallest_crew_they_can_join_and_a_tie_to_the_first_listed():
    placed = with_crews([lane("a", pooled=True), lane("b", pooled=True), lane("p", crews=("a", "b")), lane("q", crews=("a", "b")),
                         lane("r", crews=("a", "b")), lane("s", group="b"), lane("t", crews=("a", "b")), lane("u", crews=("b",))])
    assert {x.id: x.group for x in placed if not x.pooled} == {"p": "a", "q": "b", "r": "a", "s": "b", "t": "a", "u": "b"}
    assert all(not x.crews for x in placed)
    assert with_crews(placed) == placed                                             # placed once: a later chapter leaves them


def test_a_crew_not_declared_before_the_person_or_a_group_beside_crews_is_refused():
    with pytest.raises(ValueError, match="lane p: crews a are not pooled lanes declared before it"):
        with_crews([lane("p", crews=("a",)), lane("a", pooled=True)])
    with pytest.raises(ValueError, match="lane p: sets both group and crews"):
        with_crews([lane("a", pooled=True), lane("p", crews=("a",), group="a")])


def test_the_shipped_people_are_placed_one_to_a_crew_in_turn(shipped_opening: Opening):
    placed = {x.id: x.group for x in shipped_opening.lanes if x.group is not None and x.id in PEOPLE}
    assert placed == {"n2": "g_field", "n4": "g_hearth", "n5": "g_field", "n6": "g_hearth", "n7": "g_field", "n8": "g_hearth",
                      "n9": "g_field", "n10": "g_hearth", "n11": "g_hearth", "n12": "g_field"}


def test_a_hand_written_card_stands_for_the_town_card_on_its_own_lane(shipped_opening: Opening):
    cards = {c.id: c for c in shipped_opening.cards}
    assert cards["n2_watch"].label_key == "c_n2_watch" and cards["n5_watch"].label_key == "c_lane_watch"
    check_groups(shipped_opening)
    with pytest.raises(ValueError, match=r"town card \{lane\}_watch: own lane n13 has no hand-written card n13_watch on it"):
        check_groups(on_lanes(shipped_opening, "{lane}_watch", "n13").model_copy(update={"town_cards": [
            tc.model_copy(update={"own": [*tc.own, "n13"]}) if tc.id == "{lane}_watch" else tc
            for tc in on_lanes(shipped_opening, "{lane}_watch", "n13").town_cards]}))
