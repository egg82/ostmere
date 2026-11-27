"""Day twenty-two's checks on its played routes (docs/design/week-four-plan.md, items 7 and 10; verdicts.py): each push
route plays from T13's visit to B19's, week four's first chapter and the edge of written content; the walk is shown
at T13 and B18 lands at its first finish after the turn; B19 waits on its count and both its clocks; a route that takes
rules writes the film's chip rule, which no order card offers; every chip shown has a cure; the babysitter ends level
with the whenever player from the visit before T13's to an hour past B19; and typical's save at day nineteen's end,
written under the rules without day twenty-two, loads under today's and plays on with nobody deciding. The rhythm is the
readouts' (test_weektwo_readouts.py). Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import CardId, ChipId, Order, TapCard
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules19
from tests.weektwo.routes import TWENTYTWO_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
TURN_S = 504 * 3600
"""I1, the season's turn, on the calendar (week-four-numbers.md, "Landing bands")."""
B19_CLOCK_S = TURN_S + 30 * 3600
PACE_S = 3 * 3600
"""B19's two clocks: the season's thirtieth hour, and three hours after I4."""
TOOL_ROUTES = ("typical", "sharp", "whenever")


def test_a_save_from_day_nineteens_end_loads_under_day_twenty_two_and_plays_on(rebased_nineteen: Rebased):
    r = rebased_nineteen
    assert fired(r.before, rules19(), "t_t13"), "the replay under day nineteen's rules reached T13"
    assert fired(r.loaded, rules3(), "t_walk_shown"), "the walk shows at the load, T13 behind it"
    assert fired(r.later, rules3(), "t_i1"), "the season turns a day on"
    assert not fired(r.later, rules3(), "t_b18"), "B18 waits on a walk, which nobody set out on"


@pytest.mark.parametrize("twentytwo_route", TWENTYTWO_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_twenty_two_to_b19(twentytwo_route: Route):
    name, p = twentytwo_route
    assert p.stop_beat() == "B19" and "B19" in p.seen_at, f"{name} saw B19"
    assert {"I1", "B18", "SL29", "I2", "I3", "I4", "SL30"} <= set(p.landed_at), name


@pytest.mark.parametrize("twentytwo_route", TWENTYTWO_PUSH_ROUTES, indirect=True)
def test_b18_lands_at_a_walk_after_the_turn_and_b19_on_its_clocks(twentytwo_route: Route):
    name, p = twentytwo_route
    start = p.history[0][0].time
    assert p.landed_at["B18"] - start >= TURN_S, f"{name}: no walk before the turn"
    assert p.landed_at["B19"] - start >= B19_CLOCK_S, f"{name}: B19 on the season's thirtieth hour"
    assert p.landed_at["B19"] - p.landed_at["I4"] >= PACE_S, f"{name}: B19 three hours after I4"


@pytest.mark.parametrize("twentytwo_route", TOOL_ROUTES, indirect=True)
def test_a_route_that_takes_rules_writes_the_films_rule(twentytwo_route: Route):
    """No order card offers it (D-155): the route writes the chip's own condition, tapping her wash."""
    name, p = twentytwo_route
    when = next(c.when for c in p.rules.chips if c.id == ChipId("ashed"))
    assert Order(when, TapCard(CardId("n3_wash_meat"))) in p.save.orders, name


def test_every_chip_shown_in_day_twenty_two_has_a_cure(twentytwo_cures: list[str]):
    assert twentytwo_cures == []


def test_the_babysitter_ends_level_across_day_twenty_two(two_am_twentytwo_run: tuple[Measured, Measured]):
    assert compare(*two_am_twentytwo_run) == []
