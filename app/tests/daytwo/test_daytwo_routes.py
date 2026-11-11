"""Day two's checks on every route a run plays (routes.py; verdicts.py): the story's order, a tool user's B4 lag behind
the babysitter's and the typical route's cap loss; and the play's own correctness. The route's rhythm is its readout
(report.py)."""
import pytest

from ashfall_app.engine import AfterTime, TapCard, Unlock, UnlockKind, view
from tests.daytwo import content as c
from tests.daytwo.checks import day_visits
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import plays
from tests.daytwo.verdicts import CHECKS
from tests.dayone.human import lands_within, thresholds
from tests.dayone.repeats import repeated

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Verdicts = tuple[str, int, dict[str, list[str]]]
CHAIN = ("l_her_row", "l_her_first", "l_stool_1", "l_stool_2", "l_name", "l_evening_2", "l_night_2a", "l_night_2b",
         "l_morning_3", "l_room_1", "l_room_2", "l_shelter", "l_offer_1", "l_offer_2")
"""The lines on B4's way, which every route meets."""
ANSWER_LINES = {c.GO: ("l_yes", "l_walk_go", "l_b4_1"), c.SHE_GOES: ("l_she_goes", "l_b4_h1")}


@pytest.mark.parametrize("check", sorted(CHECKS))
@pytest.mark.parametrize("day2_verdicts", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_a_route_meets_the_bar(day2_verdicts: Verdicts, check: str):
    _, _, found = day2_verdicts
    assert found[check] == []


@pytest.mark.parametrize("day2_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_what_lands_away_is_seen_on_return(day2_route: DayTwoPlayer):
    p = day2_route
    for beat, t in p.seen_at.items():
        assert t >= p.landed_at[beat]
    away = [b for b, t in p.landed_at.items() if b in c.DAY_TWO_IDS and not any(v.start <= t <= v.end for v in p.visits)]
    assert all(p.seen_at[b] in {v.start for v in p.visits} for b in away if b in p.seen_at)


@pytest.mark.parametrize("day2_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_the_day_runs_on_her_lane_and_the_answer_given(day2_route: DayTwoPlayer):
    """Her default rule is installed at B3, the chain's lines all fire, and B4's lines are the set of the answer this
    route gave (chosen by the answer's state, never its text)."""
    p = day2_route
    fired = {ln.key for ln in p.lines}
    assert any(isinstance(o.when, AfterTime) and isinstance(o.then, TapCard) and o.then.card in c.TASKS
               for o in p.save.orders), p.schedule.name
    assert set(CHAIN) <= fired, sorted(set(CHAIN) - fired)
    answer = p.knobs2.answer
    assert Unlock(UnlockKind.ANSWER, answer) in p.save.unlocked
    other = c.SHE_GOES if answer == c.GO else c.GO
    assert set(ANSWER_LINES[answer]) <= fired and not set(ANSWER_LINES[other]) & fired


@pytest.mark.parametrize("day2_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_the_walks_news_lands_part_way_through_it_on_either_answer(day2_route: DayTwoPlayer):
    p = day2_route
    at = {str(ln.key): ln.time for ln in p.lines}
    answered = at["l_walk_go"] if p.knobs2.answer == c.GO else at["l_she_goes"]
    assert answered < at["l_walk_out"] < p.landed_at["B4"]


@pytest.mark.parametrize("day2_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_no_line_repeats_in_a_save(day2_route: DayTwoPlayer):
    assert repeated(day2_route.rules, day2_route.lines) == []


@pytest.mark.parametrize("day2_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_a_day_two_visit_ends_once_nothing_of_the_players_lands_within_the_dead_gap(day2_route: DayTwoPlayer):
    """A day-two visit that ends before its scheduled stop ends with no tap of the player's landing within the dead
    gap, and every route but one that stays ends at least one that way (the babysitter's ends LINGER_S after B4)."""
    p = day2_route
    assert p.end_at is not None
    gap = thresholds().dead_gap_s()
    early: list[int] = []
    for v in day_visits(p)[:-1] if p.knobs2.stays else day_visits(p):
        planned = p.schedule.visits[v.index - 1]
        if v.end < p.end_at + planned.start + planned.length:
            assert v.exit is not None and not lands_within(view(v.exit, p.rules), p.rules, v.end, gap), f"V{v.index}"
            early.append(v.index)
    assert bool(early) is not p.knobs2.stays, early
