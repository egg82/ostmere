"""Week two's checks on its played routes through day twelve, to night 14 (docs/design/week-two-plan.md, item 13;
verdicts.py): each of day twelve's push routes plays from B11's visit to S4's, the edge of week two's content; dusk 14
lands at 330 h on the calendar and S4 before B13's turn; the bear's hunts end with their pool; its days note written
at its beat's landing; away from the chapter's end no gathered store loses over half its making to its cap; every chip
shown has a cure; the babysitter ends no further ahead than the whenever player from B11's visit to an hour past S4;
and typical's save at day eleven's end, written under the rules without day twelve, loads under today's and plays on.
The rhythm is the readouts' (test_weektwo_readouts.py)."""
import pytest

from ashfall_app.engine import StoreId, Unlock, UnlockKind, units
from ashfall_app.engine.rates import store_value
from ashfall_app.engine.work import completions
from tests.daythree import counters
from tests.daythree.content import opening3, rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weekone.test_weekone_journal import misplaced_notes
from tests.weektwo import content as w2
from tests.weektwo import verdicts
from tests.weektwo.rebased import PLAYED_ON_S, Rebased, fired, rules11
from tests.weektwo.routes import TWELVE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
Counts = tuple[DayTwoPlayer, list[counters.Counts]]
DUSK_14_S = 330 * 3600
B13_S = 336 * 3600


@pytest.mark.parametrize("twelve_route", TWELVE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_twelve_to_s4(twelve_route: Route):
    name, p = twelve_route
    assert p.stop_beat() == "S4" and "S4" in p.seen_at, f"{name} saw S4"
    assert {"S1", "SL20", "S2", "B12", "S3", "N14", "A32"} <= set(p.landed_at)


@pytest.mark.parametrize("twelve_route", TWELVE_PUSH_ROUTES, indirect=True)
def test_day_twelves_days_note_is_written_at_its_beats_landing(twelve_route: Route):
    name, p = twelve_route
    days = {e.id for e in opening3().entries if e.section == "days"}
    mine = {n.id for n in opening3().notes if n.entry in days and n.beat == "B12"}
    assert mine == {"n_day_b12"}
    assert all(Unlock(UnlockKind.NOTE, n) in p.unlocked_at for n in mine), name
    assert misplaced_notes(p, opening3())[1] == [], name


@pytest.mark.parametrize("twelve_route", TWELVE_PUSH_ROUTES, indirect=True)
def test_night_14_is_held_to_the_calendar(twelve_route: Route):
    name, p = twelve_route
    start = p.history[0][0].time
    assert p.landed_at["N14"] - start == DUSK_14_S, f"{name}: dusk 14 at 330 h"
    assert DUSK_14_S < p.landed_at["S4"] - start < B13_S, f"{name}: S4 inside night 14, before B13"


@pytest.mark.parametrize("twelve_route", ["typical"], indirect=True)
def test_the_bears_hunts_end_with_their_pool(twelve_route: Route):
    """A fight card may not have a cap: its finite pool ends it, and the route's share leaves the mix once it is spent."""
    _, p = twelve_route
    s = verdicts.exit_save(p, verdicts.TWELVE)
    assert completions(s, p.rules, w2.HUNT_BEAR) == 6 and store_value(s, w2.BEAR_SIGN) == 0
    base = next(m for m in s.mixes if m.id == s.active)
    assert all(getattr(c, "card", None) != w2.HUNT_BEAR for c in base.components)


@pytest.mark.xfail(strict=True, reason=verdicts.TRACK_STONES_GAP + "; " + verdicts.HUNT_PELT_GAP)
def test_no_gathered_store_loses_over_half_its_making_away_from_day_twelves_end(twelve_loss: dict[str, tuple[int, ...]]):
    assert twelve_loss == {}


def test_every_chip_shown_in_day_twelve_has_a_cure(twelve_cures: list[str]):
    assert twelve_cures == []


def test_the_babysitter_ends_no_further_ahead_across_day_twelve(two_am_twelve_run: tuple[Measured, Measured]):
    assert compare(*two_am_twelve_run) == []


def test_a_save_from_day_elevens_end_loads_under_day_twelve_and_plays_on(rebased_eleven: Rebased):
    assert fired(rebased_eleven.before, rules11(), "t_b11"), "the replay under day eleven's rules reached B11"
    assert fired(rebased_eleven.loaded, rules3(), "t_dig"), "the dig opens at the load, its condition held"
    clock = StoreId("dig_clock")
    assert store_value(rebased_eleven.later, clock) - store_value(rebased_eleven.loaded, clock) == units(PLAYED_ON_S // 3600)
    assert fired(rebased_eleven.later, rules3(), "t_bear_sign"), "SL20 lands on the chapter's clock with nobody deciding"
    assert not fired(rebased_eleven.later, rules3(), "t_s1"), "the dig waits for its order card"
