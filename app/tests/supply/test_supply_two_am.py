"""The 2 AM test (dayone/parity.py) with the filling card in the mix, on the fixture outpost: the babysitter, given the
whenever player's reveals, who taps the staged build the second a stage can be paid, ends level with the whenever
player, whose mix kept the filler running and whose queue built the stages across the night, with the upkeep and the
raid drawing the outpost's store the while. The probes show the measure can tell: a build first shown in the night,
which nothing could queue, leaves the babysitter ahead, as does the same player with no queue."""
from typing import Unpack

from ashfall_app.engine import CardShare, SetQueue, Verb, advance, new_save, view
from tests.dayone.parity import Measured, babysat, compare, replay
from tests.dayone.sinks import SINKS
from tests.supply.chapter import BUILD, HAUL, HOUR, STAGES, Knobs, rules
from tests.supply.play import Played, play

H = HOUR
VISITS = ((0, 3 * H),)
UNTIL = 40 * H
BOOSTS = (str(BUILD),)


def pair(**kw: Unpack[Knobs]) -> tuple[Played, Measured, Measured]:
    """The whenever player's visit, and its log replayed to UNTIL as played and as the babysitter plays it."""
    p = play(VISITS, SINKS["whenever"], UNTIL, **kw)
    r, start = rules(**kw), new_save(rules(**kw))
    return p, replay(r, start, p.log, UNTIL, False, boosts=BOOSTS), replay(r, start, babysat(p.log), UNTIL, True, boosts=BOOSTS)


def test_the_babysitter_ends_no_further_ahead_with_the_filler_mixed_and_the_build_queued():
    p, w, b = pair()
    assert w.landed.get(f"{BUILD}#{STAGES}") is not None, "the whenever player's queue built every stage"
    assert any(isinstance(v, SetQueue) for _, v in p.log)
    assert compare(w, b) == []


def test_the_filler_is_in_the_players_mix_while_it_is_away():
    p, w, _ = pair()
    assert any(isinstance(c, CardShare) and c.card == HAUL for m in w.save.mixes if m.id == w.save.active for c in m.components)
    assert w.save.time == UNTIL and p.save.time == UNTIL


def test_the_replay_is_the_play():
    p, w, _ = pair()
    assert w.save == p.save


def test_the_build_is_unready_when_it_is_queued():
    """It shows before the outpost's store can pay a stage, so the queue has something to wait on."""
    r = rules()
    at_queue = advance(new_save(r), r, H)
    build = next(c for c in view(at_queue, r).cards if c.card == BUILD)
    assert build.blocker is not None


def test_a_build_first_shown_in_the_night_turns_it_red():
    """The planted control: the build shows at 4 h, after the only visit, so nothing could queue it; the babysitter taps
    it the second a stage can be paid and the whenever player's camp never builds."""
    _, w, b = pair(build_at=4 * H)
    found = compare(w, b)
    assert w.landed.get(f"{BUILD}#1") is None and b.landed.get(f"{BUILD}#1") is not None
    assert any(f.startswith(f"{BUILD}#1") for f in found)


def test_a_weakened_order_language_turns_it_red():
    """The same player with no queue builds the stages later (when the babysitter would have), and the measure says so."""
    p, w, _ = pair()
    r = rules()
    bare: list[tuple[int, Verb]] = [(t, v) for t, v in p.log if not isinstance(v, SetQueue)]
    no_queue = replay(r, new_save(r), bare, UNTIL, False, boosts=BOOSTS)
    assert no_queue.landed.get(f"{BUILD}#1") is None
    assert compare(w, no_queue)
