"""A person leaves the town at the loader (engine DESIGN.txt, "LEAVES", CHOICES "Content (the loader)"). Written blind
from that part and the loader's public functions; the `kills` marker names the rows of MUTANTS_leaves.txt each test
must turn red for. Uses retire_world's chapter: t_helper is its one ruled lane, t_burn a standing action."""
import re
from pathlib import Path

from ashfall_app.engine import ActionId, LaneId
from leaves_world import kills, leave
from retire_world import close_outcome, loaded, refused

LEAVES = 'leaves = [{ lane = "t_helper", stops = ["t_burn"] }]'


def test_a_trigger_may_leave_a_ruled_lane_with_standing_actions_to_stop(tmp_path: Path):
    r = loaded(tmp_path, SEASON="false", CLOSE=LEAVES)
    assert close_outcome(r).leaves == (leave(LaneId("t_helper"), (ActionId("t_burn"),)),)
    assert close_outcome(loaded(tmp_path, SEASON="false", CLOSE='leaves = [{ lane = "t_helper" }]')).leaves == \
           (leave(LaneId("t_helper"), ()),)   # stops default to none


@kills(19)
def test_a_leave_of_a_lane_that_is_not_ruled_is_refused_naming_the_trigger_and_the_lane(tmp_path: Path):
    loaded(tmp_path, SEASON="false", CLOSE=LEAVES)   # the control the refusal edits
    refused(tmp_path, re.escape("trigger t_close: leaves hands, which is not a ruled lane"),
            SEASON="false", CLOSE='leaves = [{ lane = "hands" }]')


@kills(19)
def test_a_lane_left_by_two_outcomes_is_refused_naming_the_lane(tmp_path: Path):
    second = ('[[triggers]]\nid = "t_again"\nwhen = { test = "after_time", value = 900 }\n'
              'outcome = { leaves = [{ lane = "t_helper" }] }\n')
    loaded(tmp_path, SEASON="false", CLOSE=LEAVES)
    refused(tmp_path, r"leaves t_helper, which another outcome already leaves",
            SEASON="false", CLOSE=LEAVES, EXTRA=second)


@kills(19)
def test_a_leave_on_a_cards_outcome_is_refused(tmp_path: Path):
    loaded(tmp_path, SEASON="false", CLOSE=LEAVES)
    refused(tmp_path, "only a trigger's or an answer's outcome has a person leave", OTHER=f"outcome = {{ {LEAVES} }}")


@kills(19)
def test_left_is_refused_in_an_outcomes_unlocks_as_joined_is(tmp_path: Path):
    loaded(tmp_path, SEASON="false", CLOSE=LEAVES)
    refused(tmp_path, "left", SEASON="false", CLOSE='unlocks = [{ unlock_kind = "left", id = "t_helper" }]')
