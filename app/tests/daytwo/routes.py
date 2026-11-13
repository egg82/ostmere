"""Day two's routes: day one's (tests/dayone/routes.py) but daily, each with its schedule, knobs, reaction and look kept and
played on past B3 to the visit B4 is seen in, with day two's knobs (policy.Knobs2) on top. Played once per pytest
session, in a fixture's setup (docs/engineering.md, "Fast from the start"). Her lane lands every few seconds, each
landing an engine event, so a game hour of day two costs far more than one of day one's (report.py prints each play's
CPU seconds): a push plays PUSH_ROUTES at seed 0, the nightly deep run every route at seeds 0-2."""
from functools import cache

from tests.daytwo import content as c
from tests.daytwo.policy import Knobs2
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.routes import ROUTES as DAY_ONE
from tests.dayone.schedules import HOUR, schedule
from tests.dayone.sinks import SINKS, SinkKnobs
from tests.opening.routes import DEEP

HORIZON_S = 10 * 24 * HOUR
"""Long enough for the lazy route, which sees B3 on its fourth day and returns once a day."""

ROUTES: dict[str, Knobs2] = {
    "typical": Knobs2(),
    "sharp": Knobs2(tries_early=False),
    "lazy": Knobs2(answer=c.SHE_GOES, her_task="keep", her_rule=False, tries_early=False),
    "by_hand": Knobs2(her_task="keep", her_rule=False),
    "larder_first": Knobs2(first_build="build_woodstack", answer=c.SHE_GOES),
    "evenings": Knobs2(),
    "lunch": Knobs2(answer=c.SHE_GOES),
    "return_22h": Knobs2(her_task="keep"),
    "babysitter": Knobs2(tries_early=False, stays=True),
    "whenever": Knobs2(answer=c.SHE_GOES, answer_order=True),
}
"""Day two's knobs per day-one route. typical: the shelter first, Go, her task to what the build lacks, her first rule,
an early try of each step; sharp: the same, no early tries; lazy: lets her go and never changes her task; by_hand: no
rule, no queue (day one's knobs), her task kept; larder_first: the woodstack first (the other build, as day one's other
build first), lets her go; evenings: as typical; lunch: lets her go; return_22h: her task kept; babysitter: acts the second
anything can be done; whenever: the queue and the rules, and the answer set by its order ahead (the 2 AM player)."""
PUSH_ROUTES = ("typical", "babysitter", "whenever")
SEEDS = (0, 1, 2) if DEEP else (0,)


def plays() -> list[tuple[str, int]]:
    return [(name, seed) for name in (ROUTES if DEEP else PUSH_ROUTES) for seed in SEEDS]


def play2(name: str, seed: int, sink_knobs: SinkKnobs) -> DayTwoPlayer:
    """A route played with the sinks as given: the route's own (day2), or another, to show what they change."""
    r = DAY_ONE[name]
    p = DayTwoPlayer(c.rules2(), seed=seed, schedule=schedule(r.schedule, 0, seed, HORIZON_S), knobs=r.knobs,
                     knobs2=ROUTES[name], sink_knobs=sink_knobs)
    p.reaction, p.look_s = r.reaction, r.look_s
    p.play_day(lambda end: schedule(r.schedule, end, seed, HORIZON_S))
    return p


@cache
def day2(name: str, seed: int = 0) -> DayTwoPlayer:
    return play2(name, seed, SINKS[name])
