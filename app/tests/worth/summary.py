"""What the worth readout counts from each visit's scores (tests/worth/route.py): worth as a fraction, the threshold
that sorts visits into moments, deciles, each week's moments per visit beside the opening's, and the longest stretch
with no moment. Pure: the caller supplies the visits. It sorts and fails nothing (docs/design/sim-invariants.md)."""
from collections.abc import Sequence
from dataclasses import dataclass

DAY_S = 24 * 3600
THRESHOLD = 0.25
"""A visit is a moment when tuner's mix lands the set's last goal at least this fraction later than the best setup.
Chosen from the readout's `fresh's worth by cause` lines, above where fresh's worth sits at visits with no cause: the
best setup drifting as goals near is noise, a cause moving it is a moment."""


@dataclass(frozen=True)
class VisitWorth:
    index: int
    at: int
    """Seconds into the game at the visit's exit."""
    goals: int
    """How many open goals are a choice: the set every score is over (0: none, and every score is None)."""
    best_s: float | None
    """Seconds until every goal of the set has landed under the best setup found (probe.py)."""
    keeper_s: float | None
    """... under the save's own mix; None when it never lands them all (as for the routes below)."""
    tuner_s: float | None
    fresh_s: float | None
    once_s: float | None
    causes: tuple[str, ...]
    moment: bool
    """Tuner's worth crossed THRESHOLD here, and tuner took the best setup."""
    came: float | None
    """XP the set's skills gained over the absence after, as a fraction of what the kept mix's rates promised; None for
    the last visit."""


def fraction(best_s: float, kept_s: float | None) -> float:
    """Worth as a fraction of the kept score; all of it when the kept setup never lands the set."""
    if kept_s is None:
        return 1.0
    return (kept_s - best_s) / kept_s if kept_s > 0 else 0.0


def is_moment(best_s: float, kept_s: float | None) -> bool:
    return fraction(best_s, kept_s) >= THRESHOLD


def worth_cell(best_s: float | None, kept_s: float | None) -> str:
    """'+2.4h 38%': hours later than the best setup that the set's last goal lands, and as a share of the kept score;
    'never' when the kept setup leaves a goal of the set unserved; '-' when there is no set."""
    if best_s is None:
        return "-"
    if kept_s is None:
        return "never"
    return f"{(kept_s - best_s) / 3600:+.1f}h {fraction(best_s, kept_s) * 100:.0f}%"


def deciles(values: Sequence[float]) -> list[float]:
    """The 0th, 10th, ..., 100th percentile of `values` by nearest rank; empty for none."""
    s = sorted(values)
    return [s[min(len(s) - 1, round(i * (len(s) - 1) / 10))] for i in range(11)] if s else []


def day_of(at: int) -> int:
    return at // DAY_S + 1


def longest_dry(visits: Sequence[VisitWorth], start: int, end: int) -> tuple[int, int]:
    """The longest stretch with no moment, as (from, to) in seconds into the game, from `start` to `end`."""
    marks = [start, *(v.at for v in visits if v.moment), end]
    return max(zip(marks, marks[1:]), key=lambda ab: ab[1] - ab[0])


@dataclass(frozen=True)
class Span:
    label: str
    visits: int
    moments: int

    @property
    def rate(self) -> float:
        return self.moments / self.visits if self.visits else 0.0


def spans(visits: Sequence[VisitWorth], opening_end: int) -> list[Span]:
    """The opening (visits up to `opening_end`), then each game week's visits after it."""
    first = [v for v in visits if v.at <= opening_end]
    rest = [v for v in visits if v.at > opening_end]
    weeks = sorted({(day_of(v.at) - 1) // 7 + 1 for v in rest})
    out = [Span("opening", len(first), sum(v.moment for v in first))]
    for w in weeks:
        inside = [v for v in rest if (day_of(v.at) - 1) // 7 + 1 == w]
        out.append(Span(f"week {w}", len(inside), sum(v.moment for v in inside)))
    return out
