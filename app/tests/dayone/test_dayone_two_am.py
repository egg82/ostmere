"""The 2 AM test on day one (parity.py): the babysitter given the whenever player's reveals ends level with it in
every store, every skill's XP, each rate-raising step's landing and what each store lost at its cap. The probes show
the measure can tell."""
import pytest

from ashfall_app.engine import CardId, SetQueue, TapCard, Verb, advance, new_save, view
from tests.banked.chapter import CLEAR, TRIP
from tests.banked.chapter import rules as banked_rules
from tests.banked.play import Played, play
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.parity import Measured, Present, babysat, compare, replay
from tests.dayone.player import DayOnePlayer
from tests.dayone.sinks import SINKS

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Pair = tuple[Measured, Measured]
SNARE = "set_snare"


def test_the_babysitter_ends_no_further_ahead(two_am_run: Pair):
    assert compare(*two_am_run) == []


@pytest.mark.parametrize("day_route", [("whenever", 0)], indirect=True)
def test_the_replay_is_the_play(two_am_run: Pair, day_route: DayOnePlayer):
    """The instrument measures the real run: the whenever player's own save, run on with nobody deciding, is the
    replay's to the same second."""
    w, _ = two_am_run
    assert advance(day_route.save, day_route.rules, w.save.time) == w.save
    assert compare(w, w) == []


@pytest.fixture(scope="module")
def without_queue(day_route: DayOnePlayer, two_am_run: Pair) -> tuple[Measured, Measured]:
    """The whenever player's day with and without its queue (When ready gone), to an hour past the first step its
    queue landed."""
    assert day_route.end_save is not None
    log = day_route.day_log()
    queued = [t for t, v in log if isinstance(v, SetQueue)]
    assert queued, "the whenever player used the queue"
    until = min(t for t in two_am_run[0].landed.values() if t > queued[0]) + 3600
    bare: list[tuple[int, Verb]] = [(t, v) for t, v in log if not isinstance(v, SetQueue)]
    return (replay(day_route.rules, day_route.end_save, log, until, babysit=False),
            replay(day_route.rules, day_route.end_save, bare, until, babysit=False))


@pytest.mark.parametrize("day_route", [("whenever", 0)], indirect=True)
def test_a_weakened_order_language_turns_it_red(without_queue: tuple[Measured, Measured]):
    """The probe can fail: the same player with no queue lands a queued step later, and the measure says so."""
    w, bare = without_queue
    late = [k for k in w.landed if bare.landed.get(k, 10**12) > w.landed[k]]
    assert late and compare(w, bare)


@pytest.fixture(scope="module")
def taps_moved(day_route: DayOnePlayer) -> tuple[Measured, int, int]:
    """The babysitter's replay of the whenever player's day with its snare taps moved to its next visit, to a minute past
    the last tap (the replay is the cost, so it runs in setup): the replay, that second, and the visit's start."""
    assert day_route.end_save is not None
    log = day_route.day_log()
    taps = [t for t, v in log if v == TapCard(CardId(SNARE))]
    later = next(v.start for v in day_route.visits if v.start > taps[0])
    moved = sorted(((later + 15 * taps.index(t) if v == TapCard(CardId(SNARE)) else t, v) for t, v in log),
                   key=lambda tv: tv[0])
    present = Present.of(tuple((v.start, v.end) for v in day_route.visits), moved)
    return replay(day_route.rules, day_route.end_save, babysat(moved), taps[-1] + 60, True, present), taps[-1] + 60, later


@pytest.mark.parametrize("day_route", [("whenever", 0)], indirect=True)
def test_the_babysitter_shares_only_a_glance_made_while_there(two_am_run: Pair, taps_moved: tuple[Measured, int, int]):
    """A step the whenever player tapped by hand while there lands at its own time in both replays (its glance is
    not attention); the same taps moved to its next visit leave the babysitter ahead, since it taps them while the
    player is away."""
    w, b = two_am_run
    snares = [k for k in w.landed if k.startswith(SNARE)]
    assert snares and all(w.landed[k] == b.landed[k] for k in snares)
    b2, until, later = taps_moved
    assert all(b2.landed[k] <= until < later for k in snares)



H = 3600
FIGHT_VISIT = ((0, 3 * H),)
FIGHT_END = 15 * H
"""The second the whenever player's fight card lands: past it the babysitter, who taps it again the moment it can, pays a
second run the player's one queue entry does not."""
CLEAR_BUILT = "clear#1"
NO_COMFORT = 10**9


def fight_pair(end: int = FIGHT_END, **times: int) -> tuple[Played, Measured, Measured]:
    """The banked fixture chapter with its trip a fight, a standing raid and a fight card among the sinks (the comfort
    never shown): the whenever player's three hours and its log replayed to FIGHT_END as played and as the babysitter
    plays it, who taps what the player tapped by hand while there at the player's own time."""
    p = play(FIGHT_VISIT, SINKS["whenever"], end, fights=True, comfort_at=NO_COMFORT, **times)
    r = banked_rules(fights=True, comfort_at=NO_COMFORT, **times)
    boosts, start = (str(CLEAR),), new_save(r)
    present = Present.of(FIGHT_VISIT, p.log)
    return (p, replay(r, start, p.log, end, False, boosts=boosts),
            replay(r, start, babysat(p.log), end, True, present, boosts))


def fights_run(m: Measured) -> dict[str, int]:
    """Each fight runner's whole fights since it first ran, at the replay's end."""
    return {str(f.runner): f.fought for f in view(m.save, banked_rules(fights=True, comfort_at=NO_COMFORT)).fights}


def test_the_babysitter_ends_no_further_ahead_with_fights_running_across_the_night():
    _, w, b = fight_pair()
    assert CLEAR_BUILT in w.landed, "the whenever player's queue started the fight card"
    ran = fights_run(w), fights_run(b)
    assert all(f["raid"] > 0 and f[str(TRIP)] > 0 for f in ran), "the standing raid and the held trip fought in both replays"
    assert compare(w, b) == []


def test_the_fight_replay_is_the_play():
    p, w, _ = fight_pair()
    assert w.save == p.save


def test_a_fight_card_first_shown_in_the_night_turns_it_red():
    """The planted control: the fight card shows at 4 h, after the only visit, so nothing could queue it and the
    babysitter starts it while the whenever player's camp does not."""
    _, w, b = fight_pair(end=17 * H, clear_at=4 * H)
    assert CLEAR_BUILT not in w.landed and CLEAR_BUILT in b.landed
    assert any(f.startswith(CLEAR_BUILT) for f in compare(w, b))


def test_a_weakened_order_language_turns_the_fight_replay_red():
    """The same player with no queue starts the fight card later, and the measure says so."""
    p, w, _ = fight_pair()
    r = banked_rules(fights=True, comfort_at=NO_COMFORT)
    bare: list[tuple[int, Verb]] = [(t, v) for t, v in p.log if not isinstance(v, SetQueue)]
    no_queue = replay(r, new_save(r), bare, FIGHT_END, False, boosts=(str(CLEAR),))
    assert CLEAR_BUILT not in no_queue.landed
    assert compare(w, no_queue)
