"""When a player comes back after the opening: each route's visits as (start, length), game seconds from the opening's
end. The opening is played from its start at OPENING_CLOCK on the player's real clock, so a schedule that keeps to
hours of the day (a workday player's: nothing 09:30-18:30) can place each visit; the others are gaps.

V1 is the end of the opening's own session (the end lines read, then V1_S more). A babysitter's one visit never
ends. Every list runs to HORIZON_S; the player stops once the day is done."""
import random
from dataclasses import dataclass

HOUR = 3600
MINUTE = 60
OPENING_CLOCK = 20 * HOUR
"""The opening is started at 20:00 on the player's clock (an evening, as a workday player plays)."""
HORIZON_S = 72 * HOUR
"""Long enough for the laziest route's last day-one visit (the lazy route sees B3 on its fourth day)."""
V1_S = 15 * MINUTE
VISIT_S = 12 * MINUTE


@dataclass(frozen=True)
class Visit:
    start: int
    length: int


@dataclass(frozen=True)
class Schedule:
    name: str
    visits: tuple[Visit, ...]
    """V1 first, at 0."""


def _gaps(name: str, gaps_h: list[float], length: int = VISIT_S, horizon: int = HORIZON_S) -> Schedule:
    """V1, then a visit `length` long after each gap in turn (cycled), the gap counted from the last visit's end."""
    visits = [Visit(0, V1_S)]
    i = 0
    while visits[-1].start < horizon:
        last = visits[-1]
        visits.append(Visit(last.start + last.length + round(gaps_h[i % len(gaps_h)] * HOUR), length))
        i += 1
    return Schedule(name, tuple(visits))


def _clock(name: str, times: list[float], end_at: int, length: int = VISIT_S, horizon: int = HORIZON_S) -> Schedule:
    """Visits at these hours of the player's day (24 h clock), every day, the first after V1; `end_at` is the
    opening's end in game seconds, which sets where on the clock the end falls."""
    visits = [Visit(0, V1_S)]
    end_clock = OPENING_CLOCK + end_at
    day = 0
    while visits[-1].start < horizon:
        for h in sorted(times):
            start = day * 24 * HOUR + round(h * HOUR) - end_clock
            if start >= visits[-1].start + visits[-1].length:
                visits.append(Visit(start, length))
        day += 1
    return Schedule(name, tuple(visits))


def whenever(seed: int, horizon: int = HORIZON_S) -> Schedule:
    """Opens it at random times of its own choosing: gaps of 1 to 12 h, visits of 8 to 15 min, seeded."""
    rng = random.Random(f"whenever-{seed}")
    visits = [Visit(0, V1_S)]
    while visits[-1].start < horizon:
        last = visits[-1]
        visits.append(Visit(last.start + last.length + rng.randint(1 * HOUR, 12 * HOUR),
                            rng.randint(8 * MINUTE, 15 * MINUTE)))
    return Schedule("whenever", tuple(visits))


def schedule(name: str, end_at: int, seed: int = 0, horizon: int = HORIZON_S) -> Schedule:
    """The named route's visits. typical: evenings and a night's sleep; sharp: back every hour or two, a night's
    sleep; lazy: once a day; evenings: a workday player's day (evenings, early morning, nothing 09:30-18:30); lunch: the same day
    with a lunch-break visit; return_22h: one return 22 h after the opening, then typical; babysitter: never leaves. Each runs
    to `horizon` after the end (day two plays past day one's)."""
    if name == "babysitter":
        return Schedule(name, (Visit(0, horizon),))
    if name == "whenever":
        return whenever(seed, horizon)
    if name == "evenings":
        return _clock(name, [21.5, 23, 7.5, 19, 20.5, 22.5], end_at, horizon=horizon)
    if name == "lunch":
        return _clock(name, [21.5, 23, 7.5, 12.5, 19, 20.5, 22.5], end_at, horizon=horizon)
    return _gaps(name, GAPS_H[name], 15 * MINUTE if name == "lazy" else VISIT_S, horizon)


GAPS_H: dict[str, list[float]] = {
    "typical": [3, 9, 4], "sharp": [1.5, 1.5, 2, 1.5, 8, 1.5, 2], "lazy": [24], "by_hand": [3, 9, 4],
    "return_22h": [22, *[3.0, 9.0, 4.0] * 20],
}
"""Hours between visits, cycled: a route that keeps no clock."""
