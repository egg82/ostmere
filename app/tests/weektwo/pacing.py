"""The whole game's pacing readout for a route played to the edge of written content: the day and week each spine beat
from B5 on lands, and the arrivals by kind of each calendar week to the end (dayone/daily.py's counting, the week-one
days included). A route that never lands a beat says so. It reports and judges nothing (docs/design/sim-invariants.md).
Ids, kinds and counts only (CLAUDE.md, "Never spoil the owner")."""
from collections import Counter
from collections.abc import Sequence

from tests.daythree import content as c3
from tests.daytwo import abs_band
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.absence import absence, daily
from tests.weektwo import verdicts

WEEK = 7
THINGS = tuple(k for k in absence.KINDS if k != "line")
"""What counts as a new thing: every kind of arrival but a line (daily.alive)."""


def week_one_days(p: DayTwoPlayer) -> list[Counter[str]]:
    """The arrivals of each calendar day before the days verdicts.calendar_days starts from."""
    return daily.day_counts(p.rules, p.history, p.lines, p.history[0][0].time, verdicts.WEEK_ONE_DAYS, c3.opening3())


def beat_lines(p: DayTwoPlayer) -> list[str]:
    """Each spine beat from B5 on, its day from the save's start and the week that day falls in, or that it was not reached."""
    pace = abs_band.load_pace()
    reached = abs_band.reached(p.landed_at, p.history[0][0].time, pace)
    return [f"{b:>4} day {reached[b]:5.2f} week {reached[b] / WEEK:4.2f}" if b in reached else f"{b:>4} not reached"
            for b in pace.targets]


def week_lines(days: Sequence[Counter[str]]) -> list[str]:
    """The arrivals by kind of each calendar week, the last of them the days left over, and the new things among them."""
    out = ["week days  " + " ".join(f"{k:>7s}" for k in absence.KINDS) + "  things"]
    for w in range(0, len(days), WEEK):
        c = sum(days[w:w + WEEK], Counter[str]())
        span = f"{w + 1}-{min(w + WEEK, len(days))}"
        out.append(f"{w // WEEK + 1:4d} {span:>5s} " + " ".join(f"{c[k]:7d}" for k in absence.KINDS)
                   + f"  {sum(c[k] for k in THINGS):6d}")
    return out


def text(name: str, p: DayTwoPlayer, later: Sequence[Counter[str]]) -> str:
    """The route's readout; `later` is the arrivals of the days after week one's (verdicts.calendar_days)."""
    days = [*week_one_days(p), *later]
    return "\n".join([f"pacing {name}: {len(days)} whole days played", *beat_lines(p), *week_lines(days)]) + "\n"
