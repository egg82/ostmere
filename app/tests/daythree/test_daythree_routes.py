"""Day three's checks on its played routes (docs/design/day-three-plan.md, item 7; verdicts.py): each push route plays
through day three to B5 with the track held where its knobs say; away from typical's last decision no gathered store
loses over half its making to its cap; the checks past the sinks hold over typical's saves with the real track in
them; and the babysitter ends no further ahead than the whenever player across the chapter. The long-wait reading the
readout marks (report.py) sees some of typical's returns and not all."""

import pytest

from ashfall_app.engine import CardShare, SaveMix
from tests.daythree import content as c3
from tests.daythree import counters, plumbing, verdicts
from tests.daythree.routes import PUSH_ROUTES
from tests.daytwo import checks as checks2
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
DRY_WOOD = (
    "design gap: at returns dry_wood only falls (the rack lays it when a rule latches, which ready_at does not count), "
    "so the comforts that take it show no ready time and When ready cannot wait on them")


@pytest.mark.parametrize("day3_route", PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_three_to_b5(day3_route: Route):
    name, p = day3_route
    assert p.stop_beat() == "B5" and "B5" in p.seen_at, f"{name} saw B5"
    assert {"K1", "K2", "K5", "A20"} <= set(p.landed_at)
    mixed = any(isinstance(v, SaveMix) and any(isinstance(c, CardShare) and c.card == c3.TRACK for c in v.mix.components)
                for _, _, v in p.decisions)
    assert mixed, f"{name} mixed the track"


def test_some_returns_and_not_all_are_marked_as_long_waits(day3_counts: tuple[DayTwoPlayer, list[counters.Counts]]):
    p, found = day3_counts
    marked = checks2.marks(p, verdicts.NOT_WAITS, verdicts.b4_visit(p))
    waited = [c.label for c in found if marked.get(c.label, "").startswith("wait")]
    assert waited and len(waited) < len(found), waited


def test_a_return_during_a_hearth_cure_alone_still_owes_a_decision(day3_counts: tuple[DayTwoPlayer, list[counters.Counts]]):
    """Some returns day two's reading counts as long waits have only a cure running (verdicts.NOT_WAITS)."""
    p, _ = day3_counts
    assert set(checks2.long_waits(p)) > set(checks2.long_waits(p, verdicts.NOT_WAITS))


@pytest.mark.xfail(strict=True, reason="content gap: roots loses over half its making 8 h away from day three's end; the "
                   "lane foragers n1_forage and n2_forage fill it faster than field_track takes it, and no other sink "
                   "takes roots (open-work.md, item 16)")
def test_no_gathered_store_loses_over_half_its_making_away_from_day_threes_end(day3_cap_loss: dict[str, tuple[int, ...]]):
    assert day3_cap_loss == {}


def test_the_checks_past_the_sinks_hold_with_the_real_track(day3_plumbed: plumbing.Plumbing):
    assert day3_plumbed.judged > 0 and day3_plumbed.problems == ()


@pytest.mark.xfail(strict=True, reason=DRY_WOOD + "; a babysitter starts them the moment it rises")
def test_the_babysitter_ends_no_further_ahead_across_the_chapter(two_am3_run: tuple[Measured, Measured]):
    assert compare(*two_am3_run) == []
