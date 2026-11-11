"""Day three's routes: day two's ten (daytwo/routes.py), each with its schedule and knobs, played on the rules with day
three merged, through day two and on past B4 with day three's chapter (content.day_three()) to the visit B5 is seen
in. Played once per pytest session, in a fixture's setup (docs/engineering.md, "Fast from the start")."""
from functools import cache

from tests.daythree import content as c3
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import HORIZON_S, ROUTES
from tests.dayone.routes import ROUTES as DAY_ONE
from tests.dayone.schedules import schedule
from tests.dayone.sinks import SINKS, SinkKnobs

PUSH_ROUTES = ("typical", "sharp", "babysitter", "whenever")
"""typical carries the density and cap-loss verdicts, typical and sharp the band, babysitter and whenever the 2 AM
test."""


def play3(name: str, seed: int, sink_knobs: SinkKnobs) -> DayTwoPlayer:
    r = DAY_ONE[name]
    p = DayTwoPlayer(c3.rules3(), seed=seed, schedule=schedule(r.schedule, 0, seed, HORIZON_S), knobs=r.knobs,
                     knobs2=ROUTES[name], sink_knobs=sink_knobs, laters=(c3.day_three(),))
    p.reaction, p.look_s = r.reaction, r.look_s
    p.play_day(lambda end: schedule(r.schedule, end, seed, HORIZON_S))
    return p


@cache
def day3(name: str, seed: int = 0) -> DayTwoPlayer:
    return play3(name, seed, SINKS[name])
