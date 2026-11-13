"""Day one's routes, each played once per pytest session (docs/engineering.md, "Fast from the start"): the opening as
its typical player plays it, then the route's visits (schedules.py) with its knobs (policy.Knobs). A push plays
PUSH_ROUTES at seed 0; the nightly deep run (HYPOTHESIS_PROFILE=ci) every route at seeds 0-2. Tests read a play
through the fixtures in conftest.py, never play their own."""
from dataclasses import dataclass, field
from functools import cache

from tests.dayone.parity import Measured, Present, babysat, replay
from tests.dayone.player import DayOnePlayer, route_player
from tests.dayone.policy import Knobs
from tests.dayone.schedules import schedule
from tests.opening.routes import DEEP


@dataclass(frozen=True)
class Route:
    schedule: str
    knobs: Knobs = field(default_factory=Knobs)
    reaction: tuple[int, int] = (2, 4)
    look_s: int = 15


ROUTES: dict[str, Route] = {
    "typical": Route("typical"),
    "sharp": Route("sharp", reaction=(1, 3)),
    "lazy": Route("lazy", Knobs(sits_up=False, mix_weave=False, screen_rule=False)),
    "by_hand": Route("by_hand", Knobs(rising_rule=False, queue=False, hunger_rule=False, screen_rule=False)),
    "larder_first": Route("typical", Knobs(first_build="build_larder")),
    "evenings": Route("evenings"),
    "lunch": Route("lunch"),
    "return_22h": Route("return_22h"),
    "babysitter": Route("babysitter", Knobs(rising_rule=False, queue=False, hunger_rule=False, screen_rule=False),
                        reaction=(1, 1),
                        look_s=600),
    "whenever": Route("whenever"),
}
"""typical: evenings and a night's sleep; sharp: back every hour or two; lazy: once a day; by_hand: no rule, no queue;
larder_first: the other build first; evenings: a workday player's day (nothing 09:30-18:30); lunch: with a lunch-break visit;
return_22h: one return 22 h later; babysitter: never away, acts the second anything can be done; whenever: random
times, the queue and the rules (the 2 AM test's player)."""
TOOL_USERS = frozenset({"typical", "sharp", "whenever", "evenings", "lunch", "return_22h", "larder_first"})
"""The players held to the babysit checks: they use the queue and the rules the game teaches. by_hand and lazy are
reported, and checked only to land behind (docs/design/sim-invariants.md); the babysitter is the measure itself."""
REPORTED = frozenset({"by_hand", "lazy"})
"""The routes that write no rules, reported and never held to a floor (docs/decisions/simulator.md, "Length"): the story
checks that every other route meets are not asked of them. `keeper` is not a day-one route."""
PUSH_ROUTES = ("typical", "by_hand", "babysitter", "whenever")
SEEDS = (0, 1, 2) if DEEP else (0,)


def plays() -> list[tuple[str, int]]:
    return [(name, seed) for name in (ROUTES if DEEP else PUSH_ROUTES) for seed in SEEDS]


@cache
def day(name: str, seed: int = 0) -> DayOnePlayer:
    r = ROUTES[name]
    p = route_player(schedule(r.schedule, 0, seed), r.knobs, seed)
    p.reaction, p.look_s = r.reaction, r.look_s
    p.play_day(lambda end: schedule(r.schedule, end, seed))   # a clock schedule places visits by the end's time
    return p


@cache
def two_am(seed: int = 0) -> tuple[Measured, Measured]:
    """The whenever player's day replayed as it was and as a babysitter given the same reveals, to an hour past the
    later of their B3s (parity.py)."""
    w = day("whenever", seed)
    assert w.end_save is not None
    log, until = w.day_log(), w.save.time + 3600
    present = Present.of(tuple((v.start, v.end) for v in w.visits), log)
    return (replay(w.rules, w.end_save, log, until, False),
            replay(w.rules, w.end_save, babysat(log), until, True, present))
