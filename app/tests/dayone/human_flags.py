"""What the human-paced player (human.py) records and flags over day one. Flags report, never fail. Beats and
promises appear by id only (CLAUDE.md, "Never spoil the owner").

Per session (the opening's, then each visit): the time of each notable event (a decision, or a new thing shown: a
story beat, a level, a find or unlock, a part of the page); the stretches of play past the dead-gap threshold with
none, up to the leave (the player leaves once nothing is left to act on: human.py); and at each leave, the payoffs
with a time the screen names and the story questions open, a leave naming none being a bored leave. Across the day, each
moment as earned (a better setup brings it sooner) or fixed-time, and the runs of fixed-time moments. A moment is an unlock or a
build stage finishing (a completion of a card with a cap above one; the last is the card's finish)."""
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from ashfall_app.engine import Save, Unlock, UnlockKind, view
from tests.dayone import checks
from tests.dayone.beats import questions_open
from tests.dayone.goals import drawn
from tests.dayone.human import HumanPlayer, Thresholds
from tests.dayone.player import DayOnePlayer, Stage

PAYOFFS = ("card", "full", "level")
"""The times the page draws that mean something coming: a card's countdown, a line's full-in, a skill's next level."""
EARNED, FIXED, UNKNOWN = "earned", "fixed", "unknown"


def dead_stretches(start: int, end: int, times: Iterable[int], limit: float) -> list[tuple[int, int]]:
    """Stretches of [start, end] longer than `limit` seconds between two notable moments (the ends count)."""
    marks = [start, *sorted(t for t in times if start <= t <= end), end]
    return [(a, b) for a, b in zip(marks, marks[1:]) if b - a > limit]


@dataclass(frozen=True)
class Leave:
    payoffs: tuple[tuple[str, str, int], ...]
    """(kind, id, seconds from the leave) for each time the screen names that means something coming."""
    questions: frozenset[str]


@dataclass(frozen=True)
class Session:
    label: str
    start: int
    end: int
    notables: tuple[tuple[int, str], ...]
    dead: tuple[tuple[int, int], ...]
    leave: Leave | None
    """None for the opening's session, which runs straight into V1."""


def bored(s: Session) -> bool:
    """A leave whose screen names no payoff: the player left with nothing to come back for (in place of a stretch
    held past the player's last act; orchestrator, 2026-10-23)."""
    return s.leave is not None and not s.leave.payoffs


def notables(w: checks.Window) -> list[tuple[int, str]]:
    """Decisions (not routine taps) and new things, each with a label: the story id for a beat, else its kind."""
    news = [(n.at, n.thing if n.thing.startswith("beat:") else n.thing.split(":", 1)[0]) for n in w.news]
    return sorted([*news, *((t, "decision") for t, kind, _ in w.acts if kind == "decision")])


def leave(p: DayOnePlayer, exit_save: Save) -> Leave:
    v = view(exit_save, p.rules)
    payoffs = tuple((k, i, at - exit_save.time) for k, i, at in drawn(exit_save, v, p.rules) if k in PAYOFFS)
    return Leave(payoffs, questions_open(b for b, t in p.seen_at.items() if t <= exit_save.time))


def sessions(p: DayOnePlayer, th: Thresholds) -> list[Session]:
    out: list[Session] = []
    exits = {f"V{v.index}": v.exit for v in p.visits}
    for w in [checks.opening_window(p), *checks.windows(p)]:
        found = notables(w)
        exit_save = exits.get(w.label)
        out.append(Session(w.label, w.start, w.end, tuple(found),
                           tuple(dead_stretches(w.start, w.end, (t for t, _ in found), th.dead_gap_s())),
                           None if exit_save is None else leave(p, exit_save)))
    return out


# ---------- earned and fixed-time unlocks and stages ----------

Landing = Unlock | Stage

def _since_end(p: DayOnePlayer) -> dict[Unlock, int]:
    assert p.end_at is not None
    return {u: t - p.end_at for u, t in p.unlocked_at.items() if t > p.end_at and u.kind is not UnlockKind.STORE}


def _stages_since_end(p: DayOnePlayer) -> dict[Stage, int]:
    assert p.end_at is not None
    return {s: t - p.end_at for s, t in p.stage_at.items() if t > p.end_at}


def _verdicts[K](g: dict[K, int], w: dict[K, int], margin: float) -> dict[K, str]:
    return {k: EARNED if k not in w or w[k] - t > margin else FIXED for k, t in g.items()}


def classify(good: DayOnePlayer, poor: DayOnePlayer, margin: float) -> dict[Unlock, str]:
    """Each unlock `good` lands after the opening: earned when `poor` lands it more than `margin` s later or never;
    fixed when it lands within the margin of the same time. (Both are played on the same visits, only the setup
    differs.)"""
    return _verdicts(_since_end(good), _since_end(poor), margin)


def classify_stages(good: DayOnePlayer, poor: DayOnePlayer, margin: float) -> dict[Stage, str]:
    """Each build stage `good` finishes after the opening, told apart as `classify` does unlocks."""
    return _verdicts(_stages_since_end(good), _stages_since_end(poor), margin)


def lands_behind(kinds: dict[Unlock, str]) -> bool:
    """Whether the poorer route of a `classify` lands at least one unlock measurably later than the good one, or never:
    the one check on players who skip the tools (docs/design/sim-invariants.md)."""
    return EARNED in kinds.values()


@dataclass(frozen=True)
class Moment:
    at: int
    """Seconds after the opening's end."""
    unlocks: tuple[Unlock, ...]
    label: str
    stages: tuple[Stage, ...] = ()


def moments(p: DayOnePlayer, kinds: dict[Landing, str], within: float) -> list[Moment]:
    """The unlocks and build stages `p` lands after the opening, grouped into moments (each landing within `within` s
    of the one before is the same moment to a person, as checks.one_per_moment): earned if any is, else unknown if any
    has no verdict (the good route never lands it), else fixed."""
    groups: list[list[tuple[Landing, int]]] = []
    landed: list[tuple[Landing, int]] = [*_since_end(p).items(), *_stages_since_end(p).items()]
    for item in sorted(landed, key=lambda x: x[1]):
        if groups and item[1] - groups[-1][-1][1] <= within:
            groups[-1].append(item)
        else:
            groups.append([item])
    out: list[Moment] = []
    for g in groups:
        found = {kinds.get(u, UNKNOWN) for u, _ in g}
        out.append(Moment(g[0][1], tuple(u for u, _ in g if isinstance(u, Unlock)),
                          EARNED if EARNED in found else UNKNOWN if UNKNOWN in found else FIXED,
                          tuple(s for s, _ in g if not isinstance(s, Unlock))))
    return out


def fixed_runs(found: Sequence[Moment], run_min: int) -> list[Sequence[Moment]]:
    """Runs of at least `run_min` moments in a row, all fixed-time: a stretch where nothing the player did earned an unlock or a stage."""
    runs: list[list[Moment]] = [[]]
    for m in found:
        if m.label == FIXED:
            runs[-1].append(m)
        elif runs[-1]:
            runs.append([])
    return [r for r in runs if len(r) >= run_min]


def per_day(found: Sequence[Moment]) -> dict[int, Counter[str]]:
    """Day 1 is the first 24 h after the opening's end."""
    days: dict[int, Counter[str]] = {}
    for m in found:
        days.setdefault(m.at // 86400 + 1, Counter())[m.label] += 1
    return days


def unlock_name(u: Unlock) -> str:
    return f"{u.kind.value}:{u.id}"


def stage_name(s: Stage) -> str:
    return f"stage:{s[0]}#{s[1]}"


def human_unlocks(p: HumanPlayer, good: DayOnePlayer, poor: DayOnePlayer, th: Thresholds) -> list[Moment]:
    margin = th.v("unlock_margin_s")
    return moments(p, {**classify(good, poor, margin), **classify_stages(good, poor, margin)}, margin)
