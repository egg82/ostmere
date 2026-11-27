"""Day twenty-seven's checks on its played routes (docs/design/week-four-plan.md, items 7, 10 and 14; verdicts.py): each
push route plays from B21's visit to I13's, week four's last chapter and the edge of written content; I11, SL36, I12 and
A40 land before I13, and I13 not before dusk 28; Lucy's last job is answered both ways across the routes; every chip
shown has a cure; the babysitter ends level with the whenever player from the visit before B21's to an hour past I13;
and typical's save at day twenty-five's end, written under the rules without day twenty-seven, loads under today's and
plays on with nobody deciding. The rhythm is the readouts' (test_weektwo_readouts.py). Ids only (CLAUDE.md, "Never
spoil the owner")."""
import pytest

from ashfall_app.engine import AnswerOffer, CardId
from ashfall_app.engine.work import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules25
from tests.weektwo import weekfour as w4
from tests.weektwo.routes import TWENTYSEVEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
DUSK_28_S = 2397600
"""t_night_28's instant: dusk on the calendar's twenty-eighth day."""


def test_a_save_from_day_twenty_fives_end_loads_under_day_twenty_seven_and_plays_on(rebased_twentyfive: Rebased):
    r = rebased_twentyfive
    assert fired(r.before, rules25(), "t_b21"), "the replay under day twenty-five's rules reached B21"
    assert fired(r.later, rules3(), "t_board"), "the board is read a day on"
    assert not fired(r.later, rules3(), "t_i13"), "I13 waits on A40, which nobody tapped"


@pytest.mark.parametrize("twentyseven_route", TWENTYSEVEN_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_twenty_seven_to_i13(twentyseven_route: Route):
    name, p = twentyseven_route
    assert p.stop_beat() == "I13" and "I13" in p.seen_at, f"{name} saw I13"
    assert {"I11", "SL36", "I12", "A40"} <= set(p.landed_at), name
    assert completions(p.save, p.rules, w4.SIT_NAMES) == 1, f"{name}: A40 sat"


@pytest.mark.parametrize("twentyseven_route", TWENTYSEVEN_PUSH_ROUTES, indirect=True)
def test_i13_lands_in_night_28(twentyseven_route: Route):
    name, p = twentyseven_route
    assert p.landed_at["I13"] >= DUSK_28_S, f"{name}: I13 at {p.landed_at['I13'] / 3600:.1f} h"


def test_typical_and_sharp_answer_the_last_job_each_way():
    given = {"no" if w4.LAST_JOB_NO.get(r) == w4.LAST_JOB else "yes" for r in ("typical", "sharp")}
    assert given == {"yes", "no"}


@pytest.mark.parametrize("twentyseven_route", ("typical", "sharp"), indirect=True)
def test_the_route_answers_the_last_job_its_way(twentyseven_route: Route):
    name, p = twentyseven_route
    given = {str(v.answer) for _, _, v in p.decisions if isinstance(v, AnswerOffer) and str(v.offer) == w4.LAST_JOB}
    no = w4.LAST_JOB_NO.get(name) == w4.LAST_JOB
    assert given == {f"{w4.LAST_JOB}_{'no' if no else 'yes'}"}, name
    assert completions(p.save, p.rules, CardId("far_snares")) == (0 if no else 1), name


def test_every_chip_shown_in_day_twenty_seven_has_a_cure(twentyseven_cures: list[str]):
    assert twentyseven_cures == []


def test_the_babysitter_ends_level_across_day_twenty_seven(two_am_twentyseven_run: tuple[Measured, Measured]):
    assert compare(*two_am_twentyseven_run) == []
