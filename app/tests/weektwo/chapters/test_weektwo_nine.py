"""Week two's checks on its played routes through day nine (docs/design/week-two-plan.md, item 13; verdicts.py): each of
day nine's push routes plays from B9's visit to B10's; away from the
chapter's end no gathered store loses over half its making to its cap; the babysitter ends no further ahead than the
whenever player from B9's visit to an hour past B10; and typical's save at day eight's end, written under the rules
without day nine, loads under today's and plays on. The rhythm is the readouts' (test_weektwo_readouts.py)."""
import pytest

from tests.daythree import counters
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.pacing.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules8
from tests.weektwo.routes import NINE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
Counts = tuple[DayTwoPlayer, list[counters.Counts]]


@pytest.mark.parametrize("nine_route", NINE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_nine_to_b10(nine_route: Route):
    name, p = nine_route
    assert p.stop_beat() == "B10" and "B10" in p.seen_at, f"{name} saw B10"
    assert {"E1", "E2", "E3", "SL18"} <= set(p.landed_at)


def test_the_babysitter_ends_no_further_ahead_across_day_nine(two_am_nine_run: tuple[Measured, Measured]):
    assert compare(*two_am_nine_run) == []


def test_a_save_from_day_eights_end_loads_under_day_nine_and_plays_on(rebased_eight: Rebased):
    assert fired(rebased_eight.before, rules8(), "t_b9"), "the replay under day eight's rules reached B9"
    assert not fired(rebased_eight.loaded, rules3(), "t_ring")
    assert fired(rebased_eight.later, rules3(), "t_ring") and fired(rebased_eight.later, rules3(), "t_gap_fire")
