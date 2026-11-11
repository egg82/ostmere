"""The 2 AM test with a trip mixed and a comfort queued (dayone/parity.py), on the fixture chapter: the babysitter given
the whenever player's reveals, who taps the comfort the second it can, ends level with the whenever player, whose queue
built it across the night. The probes show the measure can tell: a comfort first shown in the night, which no queue
could wait on, leaves the babysitter ahead, as does the same player with no queue."""
from typing import Unpack

from ashfall_app.engine import SetQueue, Verb, advance, new_save, view
from tests.banked.chapter import COMFORT, Times, rules
from tests.banked.play import Played, play
from tests.dayone.parity import Measured, babysat, compare, replay
from tests.dayone.sinks import SINKS

H = 3600
VISITS = ((0, H),)
UNTIL = 20 * H
BOOSTS = (str(COMFORT),)


def pair(**times: Unpack[Times]) -> tuple[Played, Measured, Measured]:
    """The whenever player's visit, and its log replayed to UNTIL as played and as the babysitter plays it."""
    p = play(VISITS, SINKS["whenever"], UNTIL, **times)
    r, start = rules(**times), new_save(rules(**times))
    w = replay(r, start, p.log, UNTIL, False, boosts=BOOSTS)
    b = replay(r, start, babysat(p.log), UNTIL, True, boosts=BOOSTS)
    return p, w, b


def test_the_babysitter_ends_no_further_ahead_with_a_trip_mixed_and_a_comfort_queued():
    _, w, b = pair()
    assert "comfort#1" in w.landed, "the whenever player's queue built the comfort"
    assert compare(w, b) == []


def test_the_comfort_is_unready_when_it_is_queued():
    """It shows before it can be afforded, so the queue has something to wait on (the engine's rule for every sink)."""
    p, _, _ = pair()
    r = rules()
    at_queue = advance(new_save(r), r, H)
    comfort = next(c for c in view(at_queue, r).cards if c.card == COMFORT)
    assert comfort.blocker is not None and any(isinstance(v, SetQueue) for _, v in p.log)


def test_the_replay_is_the_play():
    p, w, _ = pair()
    assert w.save == p.save


def test_a_comfort_first_shown_in_the_night_turns_it_red():
    """The planted control: the comfort shows at 2 h, after the only visit, so nothing could queue it and the
    babysitter builds it while the whenever player's camp does not."""
    _, w, b = pair(comfort_at=2 * H)
    found = compare(w, b)
    assert "comfort#1" not in w.landed and "comfort#1" in b.landed
    assert any(f.startswith("comfort#1") for f in found)


def test_a_weakened_order_language_turns_it_red():
    """The same player with no queue builds the comfort later (when the babysitter would have), and the measure says so."""
    p, w, _ = pair()
    r = rules()
    bare: list[tuple[int, Verb]] = [(t, v) for t, v in p.log if not isinstance(v, SetQueue)]
    no_queue = replay(r, new_save(r), bare, UNTIL, False, boosts=BOOSTS)
    assert "comfort#1" not in no_queue.landed
    assert compare(w, no_queue)
