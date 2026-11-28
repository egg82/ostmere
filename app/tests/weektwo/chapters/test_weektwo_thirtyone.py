"""Day thirty-one's checks on its played routes (docs/design/week-five-plan.md, item 10; verdicts.py): each push route plays
from B23's visit to B24's, week five's third chapter and the edge of written content; Y8, Y9, Y10, Y11 and A43 land before
B24, and P5 is built to its last stage; every chip shown has a cure; the babysitter ends level with the whenever player
from the visit before B23's to an hour past B24; and typical's save at day thirty's end, written under the rules without
day thirty-one, loads under today's and plays on with nobody deciding. The bands and the rhythm are the readouts' and the
shared band checks'. Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import CardId
from ashfall_app.engine.loop.work import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules30
from tests.weektwo.routes import THIRTY_ONE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]


def test_a_save_from_day_thirtys_end_loads_under_day_thirty_one_and_plays_on(rebased_thirty: Rebased):
    r = rebased_thirty
    assert fired(r.before, rules30(), "t_b23"), "the replay under day thirty's rules reached B23"
    assert all(fired(r.later, rules3(), t) for t in ("t_y8", "t_call_12h")), "t_y8 and t_call_12h on the call's clock"
    assert not fired(r.later, rules3(), "t_b24"), "t_b24 waits on the house, which nobody built"


@pytest.mark.parametrize("thirtyone_route", THIRTY_ONE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_thirty_one_to_b24(thirtyone_route: Route):
    name, p = thirtyone_route
    assert p.stop_beat() == "B24" and "B24" in p.seen_at, f"{name} saw B24"
    assert {"Y8", "Y9", "Y10", "Y11", "A43"} <= set(p.landed_at), name
    assert completions(p.save, p.rules, CardId("waystation")) == 8, name


def test_every_chip_shown_in_day_thirty_one_has_a_cure(thirtyone_cures: list[str]):
    assert thirtyone_cures == []


def test_the_babysitter_ends_level_across_day_thirty_one(two_am_thirtyone_run: tuple[Measured, Measured]):
    assert compare(*two_am_thirtyone_run) == []
