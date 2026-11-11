"""Week two's checks on its played routes through day eleven (docs/design/week-two-plan.md, items 11 and 13;
verdicts.py): each of day eleven's push routes plays from B10's visit to B11's; the family's offer joins three lanes
and the tally reads nine with the man behind them; its days notes written at their beats' landing; away from the
chapter's end no gathered store loses over half its making to its cap; the babysitter ends no further ahead than the
whenever player from B10's visit to an hour past B11; and typical's save at day nine's end, written under the rules
without day eleven, loads under today's and plays on. The rhythm is the readouts' (test_weektwo_readouts.py)."""
import pytest

from ashfall_app.engine import StoreId, Unlock, UnlockKind, units
from ashfall_app.engine.rates import store_value
from tests.daythree import counters
from tests.daythree.content import opening3, rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weekone.test_weekone_journal import misplaced_notes
from tests.weektwo import verdicts
from tests.weektwo.rebased import Rebased, fired, rules9
from tests.weektwo.routes import ELEVEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
Counts = tuple[DayTwoPlayer, list[counters.Counts]]


@pytest.mark.parametrize("eleven_route", ELEVEN_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_eleven_to_b11(eleven_route: Route):
    name, p = eleven_route
    assert p.stop_beat() == "B11" and "B11" in p.seen_at, f"{name} saw B11"
    assert {"O-family", "Z1", "O-guard", "Z2", "Z3", "A31"} <= set(p.landed_at)


@pytest.mark.parametrize("eleven_route", ["typical"], indirect=True)
def test_the_family_joins_three_lanes_and_the_tally_reads_nine(eleven_route: Route):
    _, p = eleven_route
    s = verdicts.exit_save(p, verdicts.ELEVEN)
    assert {Unlock(UnlockKind.JOINED, lane) for lane in ("n5", "n6", "n7")} <= set(s.unlocked)
    assert store_value(s, StoreId("arrivals")) == units(9)


@pytest.mark.parametrize("eleven_route", ELEVEN_PUSH_ROUTES, indirect=True)
def test_day_elevens_days_notes_are_written_at_their_beats_landing(eleven_route: Route):
    name, p = eleven_route
    days = {e.id for e in opening3().entries if e.section == "days"}
    mine = {n.id for n in opening3().notes if n.entry in days and n.beat == "B11"}
    assert mine == {"n_day_b11"}
    assert all(Unlock(UnlockKind.NOTE, n) in p.unlocked_at for n in mine), name
    assert misplaced_notes(p, opening3())[1] == [], name


@pytest.mark.xfail(strict=True, reason=verdicts.TRACK_STONES_GAP + "; " + verdicts.TRACK_ROOTS_GAP)
def test_no_gathered_store_loses_over_half_its_making_away_from_day_elevens_end(eleven_loss: dict[str, tuple[int, ...]]):
    assert eleven_loss == {}


def test_the_babysitter_ends_no_further_ahead_across_day_eleven(two_am_eleven_run: tuple[Measured, Measured]):
    assert compare(*two_am_eleven_run) == []


def test_a_save_from_day_nines_end_loads_under_day_eleven_and_plays_on(rebased_nine: Rebased):
    assert fired(rebased_nine.before, rules9(), "t_b10"), "the replay under day nine's rules reached B10"
    assert fired(rebased_nine.loaded, rules3(), "t_stranger"), "B10's arrival lands at the load, its condition held"
    clock = StoreId("stranger_clock")
    assert store_value(rebased_nine.later, clock) - store_value(rebased_nine.loaded, clock) == units(20 * 24)
    assert Unlock(UnlockKind.OFFER, "o_family") in rebased_nine.later.unlocked, "the offer waits for its answer"
