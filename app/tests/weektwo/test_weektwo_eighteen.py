"""Day eighteen's checks on its played routes (docs/design/week-three-plan.md, items 6 and 12; verdicts.py): each push
route plays from B15's visit to B16's, the edge of written content; the arrivals the table draws join on either
answer and B16 lands the morning after the fifteenth, past its sharp floor; every chip shown has a cure; the babysitter
ends no further ahead than the whenever player from the visit before B15's to an hour past B16; and typical's save at
day sixteen's end, written under the rules without day eighteen, loads under today's and plays on with nobody
deciding. The rhythm is the readouts' (test_weektwo_readouts.py). Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import StoreId, units
from ashfall_app.engine.rates import store_value
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules16
from tests.weektwo.routes import EIGHTEEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
B16_FLOOR_S = 369 * 3600
"""The fifteenth arrival's floor (week-three-numbers.md, "Landing bands"); B16 lands eight hours after him."""
STARER_HOURS = 8


def test_a_save_from_day_sixteens_end_loads_under_day_eighteen_and_plays_on(rebased_sixteen: Rebased):
    r = rebased_sixteen
    assert fired(r.before, rules16(), "t_b15"), "the replay under day sixteen's rules reached B15"
    assert fired(r.loaded, rules3(), "t_b15_clock"), "B15's clock starts at the load, B15 behind it"
    assert store_value(r.later, StoreId("b15_clock")) >= units(10), "B15's clock runs on"
    assert not fired(r.later, rules3(), "t_b16"), "B16 waits on the arrivals, who wait on answers"


@pytest.mark.parametrize("eighteen_route", EIGHTEEN_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_eighteen_to_b16(eighteen_route: Route):
    name, p = eighteen_route
    assert p.stop_beat() == "B16" and "B16" in p.seen_at, f"{name} saw B16"
    assert {"T7", "O-choir", "T8", "T9", "O-cutter", "arr15"} <= set(p.landed_at), name
    assert store_value(p.save, StoreId("arrivals")) == units(15), f"{name}: fifteen arrivals"


@pytest.mark.parametrize("eighteen_route", EIGHTEEN_PUSH_ROUTES, indirect=True)
def test_b16_lands_the_morning_after_the_fifteenth_past_its_floor(eighteen_route: Route):
    name, p = eighteen_route
    assert p.landed_at["B16"] - p.landed_at["arr15"] == STARER_HOURS * 3600, f"{name}: B16 eight hours on"
    assert p.landed_at["arr15"] - p.history[0][0].time >= B16_FLOOR_S, f"{name}: the fifteenth past 369 h"


def test_every_chip_shown_in_day_eighteen_has_a_cure(eighteen_cures: list[str]):
    assert eighteen_cures == []


def test_the_babysitter_ends_no_further_ahead_across_day_eighteen(two_am_eighteen_run: tuple[Measured, Measured]):
    assert compare(*two_am_eighteen_run) == []
