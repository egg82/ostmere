"""Day thirty's checks on its played routes (docs/design/week-five-plan.md, item 10; verdicts.py): each push route plays
from B22's visit to B23's, week five's second chapter and the edge of written content; Y4, SL38, Y5, Y6, SL39, Y7 and A42
land before B23, and B23 not before dawn 31; the cast lane completes its cast card; every chip shown has a cure; the babysitter
ends level with the whenever player from the visit before B22's to an hour past B23; and typical's save at day
twenty-nine's end, written under the rules without day thirty, loads under today's and plays on with nobody deciding.
The bands and the rhythm are the readouts' and the shared band checks'. Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import CardId
from ashfall_app.engine.loop.work import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weekfive.reads import cast_lane
from tests.weektwo import weekfive as w5
from tests.weektwo.rebased import Rebased, fired, rules29
from tests.weektwo.routes import THIRTY_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
DAWN_31_S = 2592000
"""Dawn 31 on the calendar: A42 opens once dawn_31, counting from Y6 at 708 h, is full (D-226)."""


def test_a_save_from_day_twenty_nines_end_loads_under_day_thirty_and_plays_on(rebased_twentynine: Rebased):
    r = rebased_twentynine
    assert fired(r.before, rules29(), "t_b22"), "the replay under day twenty-nine's rules reached B22"
    assert all(fired(r.later, rules3(), t) for t in ("t_track_drifts", "t_line_opens", "t_moths")), \
        "t_track_drifts and t_line_opens on outpost, and t_moths a day on"
    assert not fired(r.later, rules3(), "t_b23"), "t_b23 waits on hair, which nobody made"


@pytest.mark.parametrize("thirty_route", THIRTY_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_thirty_to_b23(thirty_route: Route):
    name, p = thirty_route
    assert p.stop_beat() == "B23" and "B23" in p.seen_at, f"{name} saw B23"
    assert {"Y4", "SL38", "Y5", "Y6", "SL39", "Y7", "A42"} <= set(p.landed_at), name
    assert p.landed_at["B23"] >= DAWN_31_S, f"{name}: B23 at {p.landed_at['B23'] / 3600:.1f} h, before dawn 31"


@pytest.mark.parametrize("thirty_route", THIRTY_PUSH_ROUTES, indirect=True)
def test_the_cast_lane_completes_its_cast_card(thirty_route: Route):
    name, p = thirty_route
    lane = cast_lane(p.save, p.rules, "tracker")
    assert lane is not None, name
    assert completions(p.save, p.rules, w5.TRACK.card_on(lane)) > 0, f"{name}: {lane} never completed its cast card"
    assert all(completions(p.save, p.rules, CardId(f"{x}_track")) == 0 for x in ("n1", "n2", "n3") if x != lane), name


def test_every_chip_shown_in_day_thirty_has_a_cure(thirty_cures: list[str]):
    assert thirty_cures == []


def test_the_babysitter_ends_level_across_day_thirty(two_am_thirty_run: tuple[Measured, Measured]):
    assert compare(*two_am_thirty_run) == []
