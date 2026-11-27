"""Day thirty's checks on its played routes (docs/design/week-five-plan.md, item 10; verdicts.py): each push route plays
from B22's visit to B23's, week five's second chapter and the edge of written content; Y4, SL38, Y5, Y6, SL39, Y7 and A42
land before B23, and B23 not before dawn 31; the cast lane completes its cast card; every chip shown has a cure; the babysitter
ends level with the whenever player from the visit before B22's to an hour past B23. No save is rebased from day
twenty-nine's end: its replay from the start would be over a save job's time alone (tools/saves_plan.py), so the earlier
chapters' rebased saves, each loaded under today's rules, stand for it. The bands and the rhythm are the readouts' and the
shared band checks'. Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import CardId
from ashfall_app.engine.work import completions
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weekfive.reads import cast_lane
from tests.weektwo import weekfive as w5
from tests.weektwo.routes import THIRTY_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
DAWN_31_S = 2592000
"""t_dawn_31's instant: A42 opens at dawn 31 on the calendar (D-226)."""


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
