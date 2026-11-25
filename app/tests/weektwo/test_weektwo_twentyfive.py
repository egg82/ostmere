"""Day twenty-five's checks on its played routes (docs/design/week-four-plan.md, items 1, 6, 7 and 10; verdicts.py):
each push route plays from B20's visit to B21's, week four's third chapter and the edge of written content; the boar
hunt runs in the mix from I8 and tells no loss before kept; both groups join, by either answer across the routes; the
post's door lifts Camp 19; every chip shown has a cure; the babysitter ends level with the whenever player from the
visit before B20's to an hour past B21; and typical's save at day twenty-three's end, written under the rules without
day twenty-five, loads under today's and plays on with nobody deciding. The rhythm is the readouts'
(test_weektwo_readouts.py). Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import AnswerOffer, CardId, Unlock, UnlockKind
from ashfall_app.engine.work import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules23
from tests.weektwo import weekfour as w4
from tests.weektwo.routes import TWENTYFIVE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
GROUPS = ("o_walkers", "o_widowers")
ANSWERING = ("typical", "sharp")
"""The routes whose answers to the groups weekfour names."""


def test_a_save_from_day_twenty_threes_end_loads_under_day_twenty_five_and_plays_on(rebased_twentythree: Rebased):
    r = rebased_twentythree
    assert fired(r.before, rules23(), "t_b20"), "the replay under day twenty-three's rules reached B20"
    assert fired(r.later, rules3(), "t_bowl_set"), "the bowl is set out a day on"
    assert not fired(r.later, rules3(), "t_b21"), "B21 waits on the groups, which nobody answered"


@pytest.mark.parametrize("twentyfive_route", TWENTYFIVE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_twenty_five_to_b21(twentyfive_route: Route):
    name, p = twentyfive_route
    assert p.stop_beat() == "B21" and "B21" in p.seen_at, f"{name} saw B21"
    assert {"I8", "I9", "O-walkers", "SL35", "I10", "O-widowers"} <= set(p.landed_at), name


@pytest.mark.parametrize("twentyfive_route", TWENTYFIVE_PUSH_ROUTES, indirect=True)
def test_the_hunt_runs_the_door_lifts_camp_19_and_both_groups_join(twentyfive_route: Route):
    name, p = twentyfive_route
    assert completions(p.save, p.rules, CardId("hunt_boar")) >= 1, f"{name}: the boar hunted"
    assert completions(p.save, p.rules, CardId("post_door")) == 1, f"{name}: the post's door hung"
    assert {Unlock(UnlockKind.ANSWERED, o) for o in GROUPS} <= set(p.save.unlocked), f"{name}: both groups answered"


def test_typical_and_sharp_answer_each_group_the_other_way():
    """Between them the two routes give every answer to both groups (weekfour.WALKERS, WIDOWERS)."""
    given = {str(w4.WALKERS[r]) for r in ANSWERING} | {str(w4.WIDOWERS[r]) for r in ANSWERING}
    assert given == {f"{o}_{a}" for o in GROUPS for a in ("food", "build")}, given


@pytest.mark.parametrize("twentyfive_route", ANSWERING, indirect=True)
def test_the_route_answers_each_group_its_way(twentyfive_route: Route):
    name, p = twentyfive_route
    given = {str(v.answer) for _, _, v in p.decisions if isinstance(v, AnswerOffer) and str(v.offer) in GROUPS}
    assert given == {str(w4.WALKERS[name]), str(w4.WIDOWERS[name])}, name


def test_every_chip_shown_in_day_twenty_five_has_a_cure(twentyfive_cures: list[str]):
    assert twentyfive_cures == []


def test_the_babysitter_ends_level_across_day_twenty_five(two_am_twentyfive_run: tuple[Measured, Measured]):
    assert compare(*two_am_twentyfive_run) == []
