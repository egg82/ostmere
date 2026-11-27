"""The 2 AM test (dayone/parity.py) with finds on the trip's completion count landing while the player is away: the
fixture chapter's trip gains FINDS finds, one at every second trip (a trigger on AtLeast(CardCount(trip), n), engine design/ "BANKED
TIME", "Finds"), and the trip's own landings are measured beside the comfort's. A trip first shown after the visit,
which nothing could mix, is the control. Not asserted: that the babysitter ends level. With the trip in the mix the
comfort comes later than the babysitter's by what the trip drinks, which is the fixture's chapter, not the measure."""
from ashfall_app.engine import new_save, value_at
from tests.banked.chapter import COMFORT, HOUR, RATE, RELICS, TRIP, rules
from tests.banked.play import Played, play
from tests.dayone.pacing.parity import Measured, babysat, replay
from tests.dayone.player.sinks import SINKS

VISITS = ((0, 3 * HOUR),)
UNTIL = 20 * HOUR
BOOSTS = (str(COMFORT), str(TRIP))
FINDS = 3


def relics(m: Measured) -> int:
    seg = next(x.segment for x in m.save.stores if x.store == RELICS)
    return value_at(seg, m.save.time) // (RATE * HOUR)


def pair(trip_at: int = HOUR // 2) -> tuple[Played, Measured, Measured]:
    """The whenever player's visit, and its log replayed to UNTIL as played and as the babysitter plays it."""
    p = play(VISITS, SINKS["whenever"], UNTIL, finds=FINDS, trip_at=trip_at)
    r = rules(finds=FINDS, trip_at=trip_at)
    start = new_save(r)
    return p, replay(r, start, p.log, UNTIL, False, boosts=BOOSTS), replay(r, start, babysat(p.log), UNTIL, True, boosts=BOOSTS)


def test_a_trip_in_the_mix_lands_finds_while_the_player_is_away():
    """The visit mixes the trip; its completions and the finds on their count land in the night, and the replay the 2 AM
    test measures from (the log applied event by event) is the play, so a find that lands away is measured the same."""
    p, w, _ = pair()
    away = [k for k, t in w.landed.items() if k.startswith(f"{TRIP}#") and t > VISITS[0][1]]
    assert away and relics(w) >= 1
    assert w.save == p.save


def test_a_trip_first_shown_in_the_night_lands_no_find_in_the_replay():
    """The control: shown at 4 h, after the only visit, nothing mixes the trip, so no trip lands and no find with it."""
    p, w, _ = pair(trip_at=4 * HOUR)
    assert not [k for k in w.landed if k.startswith(f"{TRIP}#")] and relics(w) == 0
    assert w.save == p.save
