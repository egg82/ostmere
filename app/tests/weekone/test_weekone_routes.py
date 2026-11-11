"""Week one's checks on its played routes (docs/design/days-four-to-seven-plan.md, item 1; combat-plan.md, items 9 and
10; verdicts.py): each push route plays days four to six to G2; night 7 falls before the season's turn on every route;
away from each chapter's end no gathered store loses over half its making to its cap; the checks past the sinks hold
over typical's saves; and the babysitter ends no further ahead than the whenever player across days four to six. When
the beats land, each calendar day's arrivals and each visit's counts are the readouts' (report.py)."""

import pytest

from ashfall_app.engine import CardShare, SaveMix, advance, view
from tests import readout_snapshot as rs
from tests.daythree import counters, plumbing
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weekone import content as w1
from tests.weekone import report, verdicts
from tests.weekone.routes import PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
Counts = tuple[DayTwoPlayer, list[counters.Counts]]
Checks = tuple[plumbing.Plumbing, dict[str, dict[str, tuple[int, ...]]]]


@pytest.mark.parametrize("week_route", PUSH_ROUTES, indirect=True)
def test_the_route_plays_days_four_to_six_to_g2(week_route: Route):
    name, p = week_route
    assert p.stop_beat() == "G2" and "G2" in p.seen_at, f"{name} saw G2"
    assert {"B6", "B7", "A27", "G1", "N7"} <= set(p.landed_at)
    moved = any(isinstance(v, SaveMix) and any(isinstance(c, CardShare) and c.card == w1.HAND_ON_STONE for c in v.mix.components)
                for _, _, v in p.decisions)
    assert moved, f"{name} mixed Arcana's card on damp wood"


@pytest.mark.parametrize("week_route", PUSH_ROUTES, indirect=True)
def test_g1_lands_on_a_first_hunt_the_page_reads_as_won(week_route: Route):
    """G1's lines speak of the meat the first hunt brought home; the page reads a window's lost fights off the floored
    tally, which is under 1 after a single fight whatever the strengths."""
    name, p = week_route
    at = p.landed_at["G1"]
    last = max(i for i, (t, _, _) in enumerate(p.decisions) if t <= at)
    hunt = next(f for f in view(advance(p.decided[last], p.rules, at), p.rules).fights if f.runner == w1.HUNT)
    assert (hunt.fought, hunt.lost) == (1, 0), f"{name}: G1 lands at hunt {hunt.fought}, lost {hunt.lost}"


@pytest.mark.parametrize("week_route", PUSH_ROUTES, indirect=True)
def test_night_seven_falls_before_the_seasons_turn(week_route: Route):
    _, p = week_route
    assert verdicts.night_seven(p) == []


@pytest.mark.parametrize("week_spends", verdicts.CHAPTERS, indirect=True)
def test_a_chapter_has_visits_to_count(week_spends: tuple[DayTwoPlayer, list[int]]):
    """Its setup also reads the route's visits once, before the parts below."""
    assert len(week_spends[1]) >= 3


PARTS = [(chapter, part) for chapter, n in verdicts.PARTS.items() for part in range(n)]


@pytest.mark.parametrize("week_part", PARTS, indirect=True)
def test_a_part_of_a_chapters_counting_is_read(week_part: verdicts.Decided):
    """Each heavy step of a chapter is read in a setup of its own (verdicts.PARTS), so the test below pays for none of them."""
    assert len(week_part) <= 1


@pytest.mark.parametrize("week_counts, chapter", [(c, c) for c in verdicts.CHAPTERS], indirect=["week_counts"])
def test_a_chapters_visit_readout_is_approved(week_counts: Counts, chapter: str, week_marks: dict[str, str]):
    """After the parts above, whose readings the counts reuse (verdicts.typical_decided)."""
    _, found = week_counts
    assert len(found) >= 3, "the chapter's visits were counted"
    rs.check(f"weekone-{chapter}", report.chapter_text(chapter, found, week_marks))


STONE_DRY = ("content gap: dry_wood loses over half its making 24 h away from day four's end; hand_on_stone fills it, "
             "and over the absence only the fire and n4_watch take dry wood (open-work.md, item 24)")
HUNT_PELT = ("content gap: pelt loses over half its making 24 h away from day six's end; hunt_wolf fills it, and no "
             "sink takes pelt once pelt_bedding is built (open-work.md, item 24)")


@pytest.mark.parametrize("chapter", [pytest.param("four", marks=pytest.mark.xfail(strict=True, reason=STONE_DRY)), "five",
                                     pytest.param("six", marks=pytest.mark.xfail(strict=True, reason=HUNT_PELT))])
def test_no_gathered_store_loses_over_half_its_making_away_from_the_chapters_end(week_checks: Checks, chapter: str):
    _, loss = week_checks
    assert loss[chapter] == {}


def test_the_checks_past_the_sinks_hold_over_the_week(week_checks: Checks):
    found, _ = week_checks
    assert found.judged > 0 and found.problems == ()


@pytest.mark.xfail(strict=True, reason="a staged build takes one queue entry a stage (client game/queue.ts: a card queued is "
                   "not offered again), so the whenever player queues its next stage at a later visit and the babysitter "
                   "taps it at once: woodshed#3 129.31 h vs 113.92 h, hearth_stones#3 152.97 h vs 140.97 h; and "
                   "woodshed and pelt_bedding show, ready, while the whenever player is away (t_morning_5, t_first_pelt): "
                   "pelt_bedding#1 164.11 h vs 156.47 h")
def test_the_babysitter_ends_no_further_ahead_across_days_four_to_six(two_am_week_run: tuple[Measured, Measured]):
    assert compare(*two_am_week_run) == []
