"""Day nineteen's checks on its played routes (docs/design/week-three-plan.md, items 6 and 12; verdicts.py): each push
route plays from B16's visit to T13's, the end of week three and of written content; the road over the top comes after
B16 and B17 lands at its last stretch, where the cutter's lane leaves with no rule of his left behind; T13 lands in night
21; every chip shown has a cure; the babysitter ends no further ahead than the whenever player from the visit before
B16's to an hour past T13; and typical's save at day eighteen's end, written under the rules without day nineteen, loads
under today's and plays on with nobody deciding. The rhythm is the readouts' (test_weektwo_readouts.py). Ids only
(CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import AnswerId, CardId, TapCard, Unlock, UnlockKind
from ashfall_app.engine.counts import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weektwo.content import LAST_SUN
from tests.weektwo.rebased import Rebased, fired, rules18
from tests.weektwo.routes import NINETEEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
NIGHT_21_STEP_S = 499 * 3600
"""A38 opens an hour into night 21 on the season's clock (week-three-numbers.md, "The chain that holds each floor")."""
OVER_STRETCHES = 6


def test_a_save_from_day_eighteens_end_loads_under_day_nineteen_and_plays_on(rebased_eighteen: Rebased):
    r = rebased_eighteen
    assert fired(r.before, rules18(), "t_b16"), "the replay under day eighteen's rules reached B16"
    assert fired(r.loaded, rules3(), "t_over_shown"), "the road over the top shows at the load, B16 behind it"
    assert not fired(r.later, rules3(), "t_b17"), "B17 waits on the stretches over the top, which nobody laid"


@pytest.mark.parametrize("nineteen_route", NINETEEN_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_nineteen_to_t13(nineteen_route: Route):
    name, p = nineteen_route
    assert p.stop_beat() == "T13" and "T13" in p.seen_at, f"{name} saw T13"
    assert {"T10", "T11", "SL28", "B17", "T12", "A38"} <= set(p.landed_at), name
    assert p.landed_at["T10"] > p.landed_at["B16"], f"{name}: the road over the top comes after B16"


@pytest.mark.parametrize("nineteen_route", NINETEEN_PUSH_ROUTES, indirect=True)
def test_b17_lands_at_the_last_stretch_and_the_cutter_leaves_no_rule(nineteen_route: Route):
    name, p = nineteen_route
    at_b17 = next(s for s, _ in p.history if s.time >= p.landed_at["B17"])
    assert completions(at_b17, p.rules, CardId("cut_over")) == OVER_STRETCHES, name
    assert Unlock(UnlockKind.LEFT, "n11") in set(p.save.unlocked), f"{name}: his lane left"
    lanes = {c.id: str(c.lane) for c in p.rules.cards}
    taps = [o for o in p.save.orders if isinstance(o.then, TapCard) and lanes.get(o.then.card) == "n11"]
    assert taps == [], f"{name}: a rule on the cutter's lane outlived him"


@pytest.mark.parametrize("nineteen_route", NINETEEN_PUSH_ROUTES, indirect=True)
def test_the_last_sun_shows_after_t12_and_is_answered_in_its_visit(nineteen_route: Route):
    """O-sun (D-152) is its own moment after T12 and the route's answer is given before the next return."""
    name, p = nineteen_route
    shown = p.landed_at["O-sun"]
    assert shown > p.landed_at["T12"], f"{name}: O-sun after T12"
    answer = LAST_SUN.get(name, LAST_SUN["typical"])
    answered = next((s.time for s, _ in p.history if Unlock(UnlockKind.ANSWER, AnswerId(answer)) in set(s.unlocked)), None)
    assert answered is not None, f"{name}: O-sun answered {answer}"
    visit = next(v for v in p.visits if v.start <= p.seen_at["O-sun"] <= v.end)
    assert visit.start <= answered <= visit.end, f"{name}: answered in the visit it showed"


@pytest.mark.parametrize("nineteen_route", NINETEEN_PUSH_ROUTES, indirect=True)
def test_t13_lands_in_night_21(nineteen_route: Route):
    name, p = nineteen_route
    assert p.landed_at["T13"] - p.history[0][0].time >= NIGHT_21_STEP_S, f"{name}: T13 an hour into night 21"


def test_every_chip_shown_in_day_nineteen_has_a_cure(nineteen_cures: list[str]):
    assert nineteen_cures == []


def test_the_babysitter_ends_no_further_ahead_across_day_nineteen(two_am_nineteen_run: tuple[Measured, Measured]):
    assert compare(*two_am_nineteen_run) == []
