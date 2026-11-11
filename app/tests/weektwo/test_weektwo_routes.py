"""Week two's checks on its played routes through day eight (docs/design/week-two-plan.md, item 1; verdicts.py), and each
chapter's counting read in parts. Each push route plays from G2's visit to B9's; away from the chapter's end no
gathered store loses over half its making to its cap; and the babysitter ends no further ahead than the whenever
player from G2's visit to an hour past B9. When the beats land, what each absence opens, each visit's counts and each
calendar day's arrivals are the readouts' (test_weektwo_readouts.py)."""

import pytest

from tests.daythree import counters
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weektwo import verdicts
from tests.weektwo.routes import PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
Counts = tuple[DayTwoPlayer, list[counters.Counts]]


@pytest.mark.parametrize("eight_route", PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_eight_to_b9(eight_route: Route):
    name, p = eight_route
    assert p.stop_beat() == "B9" and "B9" in p.seen_at, f"{name} saw B9"
    assert {"B8", "U1", "U2", "U3"} <= set(p.landed_at)   # side beats wait on a route's choices


PARTS = [(chapter, part) for chapter, n in verdicts.PARTS.items() for part in range(n)]


@pytest.mark.parametrize("week_part", PARTS, indirect=True, ids=[f"{c}-{n}" for c, n in PARTS])
def test_a_part_of_a_chapters_counting_is_read(week_part: verdicts.Decided):
    """Each part of a chapter's heavy steps is read in a setup of its own (verdicts.PARTS), so the tests below pay for
    none of them."""
    assert 0 < len(week_part) <= verdicts.PART_STEPS


@pytest.mark.xfail(strict=True, reason=verdicts.TRACK_STONES_GAP)
def test_no_gathered_store_loses_over_half_its_making_away_from_the_chapters_end(eight_loss: dict[str, tuple[int, ...]]):
    assert eight_loss == {}


@pytest.mark.xfail(strict=True, reason="week one's bedding lead carries in (weekone's strict xfail: a staged build takes one "
                   "queue entry a stage and shows while the whenever player is away): pelt_bedding#1-#6 7.6-9.4 h ahead "
                   "for the babysitter, so hide_flaps#1 lands 20.2 h behind and #2-#4 0.3 h ahead, and what the order and "
                   "the bedding gather and spend downstream differs in every store, xp and waste row the comparison "
                   "lists; no day-eight step is queued")
def test_the_babysitter_ends_no_further_ahead_across_day_eight(two_am_eight_run: tuple[Measured, Measured]):
    assert compare(*two_am_eight_run) == []
