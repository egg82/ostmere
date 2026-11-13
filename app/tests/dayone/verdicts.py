"""Each of day one's invariant checks on a played route (docs/design/sim-invariants.md): the story lands in order, a
tool user's B3 lags the babysitter's only by its own gaps, every rate-raising step is queueable before it is ready,
and every time the page draws comes true. The rhythm of the route is its readout (report.py), never a check here."""
from collections.abc import Callable
from functools import cache

from tests.dayone import checks, goals
from tests.dayone.bands import b3_relative, presence_steps
from tests.dayone.player import DayOnePlayer
from tests.dayone.policy import QUEUEABLE
from tests.dayone.routes import TOOL_USERS, day

CHECKS: dict[str, Callable[[str, DayOnePlayer], list[str]]] = {
    "reaches_b3": lambda name, p: _reaches_b3(p) if name in TOOL_USERS else [],
    "story_order": lambda name, p: checks.story_order(p.landed_at, name in TOOL_USERS),
    "b3_relative": lambda name, p: _relative(p) if name in TOOL_USERS else [],
    "queueable": lambda name, p: _queueable(p) if name in TOOL_USERS else [],
    "promises": lambda _, p: goals.promise_problems(p),
}


@cache
def _steps() -> int:
    return len(presence_steps(day("babysitter").rules))


def _reaches_b3(p: DayOnePlayer) -> list[str]:
    """B3 is seen within the route's horizon (the end of its last visit); the B3-relative checks say nothing without it.
    Held on the tool users only: the routes that skip the tools are reported (the readout), never held (simulator.md)."""
    if "B3" in p.seen_at:
        return []
    assert p.end_at is not None
    return [f"B3 not seen by {(p.save.time - p.end_at) / 3600:.1f} h ({len(p.visits)} visits)"]


def _relative(p: DayOnePlayer) -> list[str]:
    """bands.b3_relative on this play: the gaps of the visits up to the one B3 was seen in."""
    seen = p.seen_at.get("B3")
    gaps = [v.gap / 3600 for v in p.visits if seen is None or v.start <= seen]
    return b3_relative(checks.b3_hours(p), checks.b3_hours(day("babysitter", p.seed)), gaps, _steps())


def _queueable(p: DayOnePlayer) -> list[str]:
    assert p.end_at is not None
    return checks.boosts_shown_unready((v for _, v in p.history), {v.start for v in p.visits if v.gap > 0},
                                       p.end_at, QUEUEABLE)


@cache
def verdicts(name: str, seed: int = 0) -> dict[str, list[str]]:
    """Every check's problems on one played route (routes.day)."""
    p = day(name, seed)
    return {check: run(name, p) for check, run in CHECKS.items()}
