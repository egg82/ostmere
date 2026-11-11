"""Day fifteen's checks on its played routes (docs/design/week-three-plan.md, items 6 and 12; verdicts.py): each push
route plays from S4's visit to B14's, the edge of written content; B13 lands on the calendar; away from the chapter's
end no gathered store loses over half its making to its cap; every chip shown has a cure; the babysitter ends no
further ahead than the whenever player from the visit before S4's to an hour past B14; and typical's save at day
twelve's end, written under the rules without day fifteen, loads under today's and plays on with nobody deciding. The
rhythm is the readouts' (test_weektwo_readouts.py). Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import CardId, Order, StoreId, TapCard, units
from ashfall_app.engine.rates import store_value
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules12
from tests.weektwo.routes import FIFTEEN_PUSH_ROUTES
from tests.weektwo import verdicts

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
B13_S = 336 * 3600
CHORES = {CardId(c) for c in ("clear_roofs", "n2_clear_roofs", "peg_flaps", "n1_peg_flaps")}
"""The last season's chore cures, whose rules B13 retires."""


def chore_rules(orders: tuple[Order, ...]) -> list[CardId]:
    return [o.then.card for o in orders if isinstance(o.then, TapCard) and o.then.card in CHORES]


def test_a_save_from_day_twelves_end_loads_under_day_fifteen_and_plays_on(rebased_twelve: Rebased):
    r = rebased_twelve
    assert fired(r.before, rules12(), "t_s4"), "the replay under day twelve's rules reached S4"
    assert fired(r.loaded, rules3(), "t_hall_shown"), "the hall is shown at the load, its condition held"
    clock = StoreId("clear_clock")
    assert fired(r.later, rules3(), "t_b13") and fired(r.later, rules3(), "t_frost"), "B13 and T1 land on the calendar"
    assert store_value(r.later, clock) >= units(18), "the season's clock runs from B13, past T2's"
    assert chore_rules(r.loaded.orders), "the save carried a chore rule into the turn"
    assert chore_rules(r.later.orders) == [], "the turn retired the last season's chore rules"
    assert not fired(r.later, rules3(), "t_walls"), "the hall waits for its order card"


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_fifteen_to_b14(fifteen_route: Route):
    name, p = fifteen_route
    assert p.stop_beat() == "B14" and "B14" in p.seen_at, f"{name} saw B14"
    assert {"B13", "SL22", "T1", "T2", "T3", "SL23"} <= set(p.landed_at), name


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_b13_is_held_to_the_calendar(fifteen_route: Route):
    name, p = fifteen_route
    assert p.landed_at["B13"] - p.history[0][0].time == B13_S, f"{name}: B13 at 336 h"


@pytest.mark.xfail(strict=True, reason=verdicts.STONE_DRY_GAP)
def test_no_gathered_store_loses_over_half_its_making_away_from_day_fifteens_end(fifteen_loss: dict[str, tuple[int, ...]]):
    assert fifteen_loss == {}


def test_every_chip_shown_in_day_fifteen_has_a_cure(fifteen_cures: list[str]):
    assert fifteen_cures == []


def test_the_babysitter_ends_no_further_ahead_across_day_fifteen(two_am_fifteen_run: tuple[Measured, Measured]):
    assert compare(*two_am_fifteen_run) == []
