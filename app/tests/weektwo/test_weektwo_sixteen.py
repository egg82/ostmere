"""Day sixteen's checks on its played routes (docs/design/week-three-plan.md, items 6 and 12; verdicts.py): each push
route plays from B14's visit to B15's, the edge of written content; B15 waits on the field stone and lands past its
sharp floor; every chip shown has a cure; the babysitter ends no further ahead than the whenever player from the visit
before B14's to an hour past B15; and typical's save at day fifteen's end, written under the rules without day
sixteen, loads under today's and plays on with nobody deciding. The rhythm is the readouts' (test_weektwo_readouts.py).
Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import StoreId, units
from ashfall_app.engine.loop.rates import store_value
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules15
from tests.weektwo.routes import SIXTEEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
B15_FLOOR_S = 349 * 3600
"""B15's sharp floor (week-three-numbers.md, "Landing bands"), held by T5's clock."""


def test_a_save_from_day_fifteens_end_loads_under_day_sixteen_and_plays_on(rebased_fifteen: Rebased):
    r = rebased_fifteen
    assert fired(r.before, rules15(), "t_b14"), "the replay under day fifteen's rules reached B14"
    assert fired(r.loaded, rules3(), "t_table_clock"), "the table's clock starts at the load, B14 behind it"
    assert store_value(r.later, StoreId("table_clock")) >= units(10), "the table's clock runs on"
    assert fired(r.later, rules3(), "t_rows_black") and fired(r.later, rules3(), "t_hall_hearth"), "T4 and SL25 land"
    assert not fired(r.later, rules3(), "t_b15"), "B15 waits for the field stone's tap"


@pytest.mark.parametrize("sixteen_route", SIXTEEN_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_sixteen_to_b15(sixteen_route: Route):
    name, p = sixteen_route
    assert p.stop_beat() == "B15" and "B15" in p.seen_at, f"{name} saw B15"
    assert {"O-road", "A36", "T4", "SL24", "SL25", "T5", "A35"} <= set(p.landed_at), name


@pytest.mark.parametrize("sixteen_route", SIXTEEN_PUSH_ROUTES, indirect=True)
def test_b15_waits_on_the_field_stone_past_its_floor(sixteen_route: Route):
    name, p = sixteen_route
    assert p.landed_at["B15"] == p.landed_at["A35"], f"{name}: B15 at the field stone's tap"
    assert p.landed_at["B15"] - p.history[0][0].time >= B15_FLOOR_S, f"{name}: B15 past 349 h"


def test_every_chip_shown_in_day_sixteen_has_a_cure(sixteen_cures: list[str]):
    assert sixteen_cures == []


def test_the_babysitter_ends_no_further_ahead_across_day_sixteen(two_am_sixteen_run: tuple[Measured, Measured]):
    assert compare(*two_am_sixteen_run) == []
