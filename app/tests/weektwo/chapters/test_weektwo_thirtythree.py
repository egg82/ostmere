"""Day thirty-three's checks on its played routes (docs/design/week-five-plan.md, items 10 and 14; verdicts.py): each push
route plays from B24's visit to Y15's, week five's last chapter and the edge of written content; Y12, Y13, A44, B25 and
Y14 land before Y15, and Y15 not before dusk 35; Lucy's last job is answered both ways across the routes; every chip
shown has a cure; the babysitter ends level with the whenever player from the visit before B24's to an hour past Y15;
past Y15 nothing in the content tells another moment; and typical's save at day thirty-one's end, written under the rules
without day thirty-three, loads under today's and plays on with nobody deciding. The bands and the rhythm are the
readouts' and the shared band checks'. Ids only (CLAUDE.md, "Never spoil the owner")."""
from functools import cache

import pytest

from ashfall_app.engine import AnswerOffer, Save, TriggerId, advance
from ashfall_app.engine.loop.work import completions
from ashfall_app.rules.schema import load_opening
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weekone import verdicts as v1
from tests.weektwo import verdicts
from tests.weektwo import weekfive as w5
from tests.weektwo.rebased import Rebased, fired, rules31
from tests.weektwo.routes import THIRTY_THREE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
DUSK_35_S = 3002400
"""t_night_35's instant: dusk on the calendar's thirty-fifth day."""
PAST_EDGE_S = 3 * 24 * 3600
"""How long past a save the edge check plays on with nobody deciding: past the next season's turn at 840 h."""


@cache
def told() -> frozenset[TriggerId]:
    """The content's triggers whose outcome tells a moment (a story line)."""
    o = load_opening()
    return frozenset(TriggerId(t.id) for t in o.triggers if any(o.line_kinds.get(k) == "story" for k in t.outcome.line_keys))


def told_after(save: Save, p: DayTwoPlayer) -> set[str]:
    """The triggers that tell a moment, fired in PAST_EDGE_S of `save` played on with nobody deciding."""
    later = advance(save, p.rules, save.time + PAST_EDGE_S)
    ids = [t.id for t in p.rules.triggers]
    return {str(i) for i, a, b in zip(ids, save.fired, later.fired) if b and not a and i in told()}


def test_a_save_from_day_thirty_ones_end_loads_under_day_thirty_three_and_plays_on(rebased_thirtyone: Rebased):
    r = rebased_thirtyone
    assert fired(r.before, rules31(), "t_b24"), "the replay under day thirty-one's rules reached B24"
    assert all(fired(r.later, rules3(), t) for t in ("t_y12", "t_y13")), "t_y12 and t_y13 on the ward's clock"
    assert not fired(r.later, rules3(), "t_b25"), "t_b25 waits on A44, which nobody tapped"


@pytest.mark.parametrize("thirtythree_route", THIRTY_THREE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_thirty_three_to_y15(thirtythree_route: Route):
    name, p = thirtythree_route
    assert p.stop_beat() == "Y15" and "Y15" in p.seen_at, f"{name} saw Y15"
    assert {"Y12", "Y13", "A44", "B25", "Y14"} <= set(p.landed_at), name
    assert completions(p.save, p.rules, w5.OPEN_WARD) == 1, f"{name}: A44 done"


@pytest.mark.parametrize("thirtythree_route", THIRTY_THREE_PUSH_ROUTES, indirect=True)
def test_y15_lands_in_night_35(thirtythree_route: Route):
    name, p = thirtythree_route
    assert p.landed_at["Y15"] >= DUSK_35_S, f"{name}: Y15 at {p.landed_at['Y15'] / 3600:.1f} h"


def test_typical_and_sharp_answer_the_last_job_each_way():
    given = {"no" if w5.LAST_JOB_NO.get(r) == w5.LAST_JOB else "yes" for r in ("typical", "sharp")}
    assert given == {"yes", "no"}


@pytest.mark.parametrize("thirtythree_route", ("typical", "sharp"), indirect=True)
def test_the_route_answers_the_last_job_its_way(thirtythree_route: Route):
    name, p = thirtythree_route
    given = {str(v.answer) for _, _, v in p.decisions if isinstance(v, AnswerOffer) and str(v.offer) == w5.LAST_JOB}
    no = w5.LAST_JOB_NO.get(name) == w5.LAST_JOB
    assert given == {f"{w5.LAST_JOB}_{'no' if no else 'yes'}"}, name
    assert completions(p.save, p.rules, w5.HILL_STAKES) == (0 if no else 1), name


@pytest.mark.parametrize("thirtythree_route", ["typical"], indirect=True)
def test_nothing_past_y15_tells_another_moment(thirtythree_route: Route):
    """Played on three days from Y15's visit with nobody deciding, no trigger with a story line fires: the end card is the
    last thing written. The control: from B24's visit the same play-on tells day thirty-three's moments."""
    _, p = thirtythree_route
    assert told_after(p.save, p) == set()
    assert {"t_y12", "t_y13"} <= told_after(v1.exit_save(p, verdicts.THIRTY_ONE), p)


def test_every_chip_shown_in_day_thirty_three_has_a_cure(thirtythree_cures: list[str]):
    assert thirtythree_cures == []


def test_the_babysitter_ends_level_across_day_thirty_three(two_am_thirtythree_run: tuple[Measured, Measured]):
    assert compare(*two_am_thirtythree_run) == []
