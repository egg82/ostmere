"""When a counted quantity first reached a level, bisected between the instants a play left saves at (the ladder
readout, tests/ladder/readout.py). Pure: the caller supplies the instants and `at`, the quantity's value at any instant."""
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

TOL_S = 60
"""The bisection stops when the bracket is this many seconds wide, and reports its upper end."""


@dataclass(frozen=True)
class Reach:
    level: int
    at: int | None
    """Seconds into the game the level was first reached, None when not by the last instant."""
    gap: int | None
    """Seconds since the previous level was reached; None when either is unreached."""


def first_reach(times: Sequence[int], at: Callable[[int], int], target: int, tol: int = TOL_S) -> int | None:
    """The first instant `at` reads `target` or more, within `tol` seconds, or None when it has not by times[-1].

    `times` ascend and `at` never falls. The first sample at or past the target is found by bisecting the samples
    (so few evaluations of `at`), then the instants between it and the one before are bisected, the upper end kept.
    """
    if not times or at(times[-1]) < target:
        return None
    lo, hi = 0, len(times) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if at(times[mid]) >= target:
            hi = mid
        else:
            lo = mid + 1
    if lo == 0:
        return times[0]
    below, above = times[lo - 1], times[lo]
    while above - below > tol:
        mid = (below + above) // 2
        if at(mid) >= target:
            above = mid
        else:
            below = mid
    return above


def reaches(times: Sequence[int], at: Callable[[int], int], levels: Iterable[int], tol: int = TOL_S) -> list[Reach]:
    """Each of `levels` (ascending) with when it was first reached and the gap from the level before it in the list;
    the first level's gap is from instant 0."""
    out: list[Reach] = []
    before: int | None = 0
    for level in levels:
        found = first_reach(times, at, level, tol)
        out.append(Reach(level, found, None if found is None or before is None else found - before))
        before = found
    return out
