"""The 2 AM test on day two (tests/dayone/parity.py's replay, with day two's builds and comfort among the boosts): the whenever
player's decisions from the exit of the visit before the one B3 is seen in are replayed twice, as they were and as a
babysitter given the same reveals, to an hour past the later B4. Her lane runs in both (her default rule needs nobody),
the answer is the whenever player's (its answer order), and the babysitter taps each build the second it can.

her_task_at_b3 is the design's other case (day-two.md, "The 2 AM test"): the babysitter makes the whenever player's
first change of her task at B3's landing instead of at that player's return. It is ahead only by the player's own
choice of task; the report prints the gap."""
from functools import cache

from ashfall_app.engine import AfterTime, Order, SetOrders, TapCard, Verb
from tests.daytwo import content as c
from tests.daytwo.player import QUEUEABLE, DayTwoPlayer
from tests.daytwo.routes import day2
from tests.dayone.parity import Measured, Present, babysat, replay

BOOSTS = (*QUEUEABLE, c.BED)
"""The queueable steps and the comfort: the babysitter builds each of its stages the second it can."""


def start(p: DayTwoPlayer) -> tuple[int, int]:
    """(the save index in history, its time): the exit of the visit before day two's V1, or V1's start."""
    first = p.b3_visit()
    assert first is not None
    t = p.visits[first - 2].end if first > 1 else p.visits[0].start
    i = next(i for i, (s, _) in enumerate(p.history) if s.time >= t)
    return i, p.history[i][0].time


def log_from(p: DayTwoPlayer, t: int) -> list[tuple[int, Verb]]:
    return [(at, verb) for at, _, verb in p.decisions if at >= t]


def until(p: DayTwoPlayer) -> int:
    assert "B4" in p.landed_at
    return p.landed_at["B4"] + 3600


def task_change(log: list[tuple[int, Verb]]) -> int | None:
    """The index of the first SetOrders that changes her default rule's task."""
    def task(v: SetOrders) -> str | None:
        return next((o.then.card for o in v.orders if isinstance(o.when, AfterTime) and isinstance(o.then, TapCard)
                     and o.then.card in c.TASKS), None)
    last: str | None = None
    for i, (_, v) in enumerate(log):
        if isinstance(v, SetOrders):
            now = task(v)
            if last is not None and now is not None and now != last:
                return i
            last = now if now is not None else last
    return None


@cache
def two_am2(seed: int = 0) -> tuple[Measured, Measured]:
    w = day2("whenever", seed)
    i, t = start(w)
    s0, log = w.history[i][0], log_from(w, t)
    present = Present.of(tuple((v.start, v.end) for v in w.visits), log)
    end = until(w)
    return (replay(w.rules, s0, log, end, False, boosts=BOOSTS),
            replay(w.rules, s0, babysat(log), end, True, present, BOOSTS))


@cache
def her_task_at_b3(seed: int = 0) -> tuple[Measured, Measured] | None:
    """The whenever replay against a babysitter whose first task change lands at B3, or None when the whenever player
    never changes her task."""
    w = day2("whenever", seed)
    i, t = start(w)
    s0, log = w.history[i][0], log_from(w, t)
    k = task_change(log)
    if k is None:
        return None
    at = max(w.landed_at["B3"], t)
    base = next((v.orders for when, v in reversed(log) if when <= at and isinstance(v, SetOrders)), s0.orders)
    changed = log[k][1]
    assert isinstance(changed, SetOrders)
    want = next(o.then for o in changed.orders if isinstance(o.when, AfterTime) and isinstance(o.then, TapCard)
                and o.then.card in c.TASKS)
    early = SetOrders(tuple(Order(o.when, want) if isinstance(o.when, AfterTime) and isinstance(o.then, TapCard)
                            and o.then.card in c.TASKS else o for o in base))
    moved = sorted([*log, (at, early)], key=lambda tv: tv[0])
    end = until(w)
    return (replay(w.rules, s0, log, end, False, boosts=BOOSTS), replay(w.rules, s0, moved, end, False, boosts=BOOSTS))
