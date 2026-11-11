"""A quantity between events: start time, start value, constant rate, and the value it stops at; for a store that card
lumps move, the work of those cards too (LumpSegment).

Quantities are read off segments, never accumulated. Every segment in a save starts at save.time.
"""
from dataclasses import dataclass

from .errors import TimeOrderError
from .units import ceil_div


@dataclass(frozen=True)
class Segment:
    """value(t) = start_value + rate * (t - start), held at `limit` once reached.

    `rate` is quantity units per second (equal to the rate per hour in rate units; see units.py). `limit` is the
    bound the motion is heading for (0, a cap, a hold level, or the last level's XP), or None when nothing stops it.
    Invariants: rate == 0 implies limit is None or limit == start_value; a non-None limit lies in the direction of
    motion (limit <= start_value when rate < 0, limit >= start_value when rate > 0).
    """

    start: int
    start_value: int
    rate: int
    limit: int | None = None


@dataclass(frozen=True)
class Lump:
    """One card's lump lines on a store: `num` / LumpSegment.den units of the store per unit of the card's `work`
    (negative for an input). The work is read clamped at its own limit, so the lump stops where the work stops."""

    work: Segment
    num: int


@dataclass(frozen=True)
class LumpSegment(Segment):
    """A store that card lumps move (DESIGN.txt, "Rate form"): value(t) = start_value + flow * (t - start)
    + floor(G(t)) - floor(G(start)), G(t) = sum(num * value_at(work, t)) / den over `lumps`, held at `limit` once
    reached. `rate` is the slope at start rounded down, flow + floor(sum(num * work.rate) / den): what a reader that
    samples linearly gets, trailing the engine by under one unit per second. Never in a save: a save keeps the plain
    Segment of its four fields, and motion.store_segment adds the work back from the save's cards."""

    flow: int = 0
    den: int = 1
    lumps: tuple[Lump, ...] = ()


def value_at(seg: Segment, t: int) -> int:
    """The segment's value at integer time t >= seg.start, clamped at seg.limit in the direction of motion.

    The clamp absorbs the overshoot of the last partial second before a bound (less than |rate| units), so a value is
    never below 0 or above its cap. Raises TimeOrderError for t < seg.start.
    """
    if t < seg.start:
        raise TimeOrderError(f"t={t} is before the segment's start {seg.start}")
    if isinstance(seg, LumpSegment):
        return _clamped(seg, _lump_value(seg, t), _direction(seg))
    return _clamped(seg, seg.start_value + seg.rate * (t - seg.start), seg.rate)


def _clamped(seg: Segment, v: int, direction: int) -> int:
    if seg.limit is not None and direction < 0:
        return max(v, seg.limit)
    if seg.limit is not None and direction > 0:
        return min(v, seg.limit)
    return v


def _direction(seg: LumpSegment) -> int:
    """The exact slope at the start, times den: its sign is the direction of motion."""
    return seg.flow * seg.den + sum(k.num * k.work.rate for k in seg.lumps)


def _scaled(seg: LumpSegment, t: int) -> int:
    """den * G(t)."""
    return sum(k.num * value_at(k.work, t) for k in seg.lumps)


def _lump_value(seg: LumpSegment, t: int) -> int:
    moved = _scaled(seg, t) // seg.den - _scaled(seg, seg.start) // seg.den
    return seg.start_value + seg.flow * (t - seg.start) + moved


def reach_time(seg: Segment, target: int) -> int | None:
    """The first integer t >= seg.start at which value_at(seg, t) has reached `target` in the direction of motion.

    Exact ceiling division: start + ceil_div(target - start_value, rate) for rising, the mirror for falling; for a
    LumpSegment, one such division per stretch between the times its cards' work stops. Returns seg.start when the
    value is already at target, and None when the motion never reaches it (wrong direction, zero rate, or a limit
    short of the target).
    """
    if isinstance(seg, LumpSegment):
        return _lump_reach(seg, target)
    v0, r, lim = seg.start_value, seg.rate, seg.limit
    if target == v0:
        return seg.start
    if r > 0 and target > v0 and (lim is None or target <= lim):
        return seg.start + ceil_div(target - v0, r)
    if r < 0 and target < v0 and (lim is None or target >= lim):
        return seg.start + ceil_div(v0 - target, -r)
    return None


def _lump_reach(seg: LumpSegment, target: int) -> int | None:
    """value(t) = base + flow * (t - start) + floor(den * G(t) / den); between the times the cards' work stops it is
    monotone, so each stretch is one ceiling division (_solve)."""
    if target == seg.start_value:
        return seg.start
    slope = _direction(seg)
    if seg.limit is not None and ((slope > 0 and target > seg.limit) or (slope < 0 and target < seg.limit)):
        return None
    up = target > seg.start_value
    a, p = seg.start, _scaled(seg, seg.start)
    base = seg.start_value - p // seg.den
    stops = sorted({t for k in seg.lumps if k.work.limit is not None and (t := reach_time(k.work, k.work.limit)) is not None})
    for b in [*stops, None]:
        dt = _solve(seg.den, p, slope, target - base - seg.flow * (a - seg.start), up)
        if dt is not None and (b is None or a + dt < b):
            return a + dt
        if b is None:
            return None
        a, p = b, _scaled(seg, b)
        slope = seg.den * seg.flow + sum(k.num * k.work.rate for k in seg.lumps
                                         if k.work.limit is None or value_at(k.work, a) < k.work.limit)
    return None


def _solve(den: int, p: int, slope: int, gap: int, up: bool) -> int | None:
    """The fewest seconds dt >= 0 for flow * dt + floor((p + s * dt) / den) to reach `gap` (from below when `up`, else
    from above), slope = s + den * flow; None when it never does. Monotone in dt, so one ceiling division."""
    if up:
        need = den * gap - p
        return 0 if need <= 0 else ceil_div(need, slope) if slope > 0 else None
    room = den * (gap + 1) - 1 - p
    return 0 if room >= 0 else ceil_div(-room, -slope) if slope < 0 else None
