"""Day twenty-nine's checks on its played routes (docs/design/week-five-plan.md, items 1, 2, 3 and 10; verdicts.py): each
push route plays from I13's visit to B22's, week five's first chapter and the edge of written content; Y1, SL37, Y2 and Y3
land before B22, and O-first-run is answered both ways across the routes; the season's turn drains the last season's
film inside the hour and its chip never shows after; the tracker is cast at B22 on every route; every chip shown has a
cure; the babysitter ends level with the whenever player from the visit before I13's to an hour past B22; and typical's
save at day twenty-seven's end, written under the rules without day twenty-nine, loads under today's and plays on with
nobody deciding. The bands and the rhythm are the readouts' and the shared band checks'. Ids only (CLAUDE.md, "Never
spoil the owner")."""
import pytest

from ashfall_app.engine import AnswerOffer, StoreId, value
from ashfall_app.engine.gates import shown_chips
from ashfall_app.engine.work import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weekfive.reads import cast_lane
from tests.weektwo import weekfive as w5
from tests.weektwo.rebased import Rebased, fired, rules27
from tests.weektwo.routes import TWENTYNINE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
TURN_S, HOUR_S = 2419200, 3600
"""t_y1's instant: the season's second turn on the calendar. A beat's landed_at is the save it is first read in, which on
a return can be hours later."""


def test_a_save_from_day_twenty_sevens_end_loads_under_day_twenty_nine_and_plays_on(rebased_twentyseven: Rebased):
    r = rebased_twentyseven
    assert fired(r.before, rules27(), "t_i13"), "the replay under day twenty-seven's rules reached I13"
    assert fired(r.later, rules3(), "t_y1") and fired(r.later, rules3(), "t_pin"), "the turn and Y3 land a day on"
    assert not fired(r.later, rules3(), "t_b22"), "B22 waits on O-first-run, which nobody answered"


@pytest.mark.parametrize("twentynine_route", TWENTYNINE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_twenty_nine_to_b22(twentynine_route: Route):
    name, p = twentynine_route
    assert p.stop_beat() == "B22" and "B22" in p.seen_at, f"{name} saw B22"
    assert {"Y1", "SL37", "Y2", "Y3", "O-first-run"} <= set(p.landed_at), name
    assert p.landed_at["Y1"] >= TURN_S, f"{name}: Y1 at {p.landed_at['Y1'] / 3600:.1f} h, before the turn"
    assert all(fired(s, p.rules, "t_y1") == (s.time >= TURN_S) for s, _ in p.history if s.time >= TURN_S - 24 * HOUR_S), \
        f"{name}: the turn fired off its instant"


@pytest.mark.parametrize("twentynine_route", TWENTYNINE_PUSH_ROUTES, indirect=True)
def test_the_tracker_is_cast_at_b22(twentynine_route: Route):
    name, p = twentynine_route
    assert cast_lane(p.save, p.rules, "tracker") is not None, name


@pytest.mark.parametrize("twentynine_route", TWENTYNINE_PUSH_ROUTES, indirect=True)
def test_the_turn_drains_the_film_inside_the_hour_and_its_chip_never_shows_after(twentynine_route: Route):
    name, p = twentynine_route
    after = [s for s, _ in p.history if s.time >= TURN_S + HOUR_S]
    assert after, f"{name}: no save an hour past the turn"
    assert all(value(s, p.rules, StoreId("film"), s.time) == 0 for s in after), name
    assert not any("ashed" in {str(c) for c in shown_chips(s, p.rules)} for s in after), name


def test_typical_and_sharp_answer_the_first_run_each_way():
    given = {str(w5.FIRST_RUN_ANSWERS.get(r, w5.FIRST_RUN_ANSWERS["typical"])) for r in ("typical", "sharp")}
    assert given == {"o_first_run_yes", "o_first_run_other"}


@pytest.mark.parametrize("twentynine_route", ("typical", "sharp"), indirect=True)
def test_the_route_answers_the_first_run_its_way(twentynine_route: Route):
    name, p = twentynine_route
    given = {str(v.answer) for _, _, v in p.decisions if isinstance(v, AnswerOffer) and v.offer == w5.FIRST_RUN_OFFER}
    yes = str(w5.FIRST_RUN_ANSWERS[name]) == "o_first_run_yes"
    assert given == {str(w5.FIRST_RUN_ANSWERS[name])}, name
    assert completions(p.save, p.rules, w5.FIRST_RUN) == (1 if yes else 0), name


def test_every_chip_shown_in_day_twenty_nine_has_a_cure(twentynine_cures: list[str]):
    assert twentynine_cures == []


def test_the_babysitter_ends_level_across_day_twenty_nine(two_am_twentynine_run: tuple[Measured, Measured]):
    assert compare(*two_am_twentynine_run) == []
