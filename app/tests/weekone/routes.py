"""Week one's routes: day three's (daythree/routes.py) played on past B5 through days four to six to the visit G2 is seen
in, one player over all four chapters (daytwo/player.laters). Played once per pytest session, in a fixture's setup
(docs/engineering.md, "Fast from the start")."""
from functools import cache

from ashfall_app.engine import Rules
from tests.daythree import content as c3
from tests.daythree.chapter import Later
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import ROUTES
from tests.dayone.routes import ROUTES as DAY_ONE
from tests.dayone.schedules import HOUR, schedule
from tests.dayone.sinks import SINKS, SinkKnobs
from tests.weekone import content as w1

HORIZON_S = 16 * 24 * HOUR
"""Long enough for the lazy route, which reaches B7 late if at all, and for week two's plays on from these, which end
at night 14 (336 h at the latest)."""
PUSH_ROUTES = ("typical", "sharp", "babysitter", "whenever")


def play_week(name: str, seed: int, sink_knobs: SinkKnobs, rules: Rules | None = None,
              laters: tuple[Later, ...] | None = None) -> DayTwoPlayer:
    """A route played through `laters` (all of week one's chapters by default) on `rules` (the content's by default)."""
    r = DAY_ONE[name]
    p = DayTwoPlayer(rules or c3.rules3(), seed=seed, schedule=schedule(r.schedule, 0, seed, HORIZON_S), knobs=r.knobs,
                     knobs2=ROUTES[name], sink_knobs=sink_knobs, laters=laters or w1.chapters())
    p.reaction, p.look_s = r.reaction, r.look_s
    p.play_day(lambda end: schedule(r.schedule, end, seed, HORIZON_S))
    return p


@cache
def week1(name: str, seed: int = 0) -> DayTwoPlayer:
    return play_week(name, seed, SINKS[name])
