"""Each of day two's invariant checks on a played route (docs/design/sim-invariants.md): its beats all land in order, a
tool user's B4 lags the babysitter's only by its own gaps. The route's rhythm is its readout (report.py)."""
from collections.abc import Callable
from functools import cache

from tests.daytwo import checks
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import day2
from tests.dayone.player.routes import TOOL_USERS


def _relative(name: str, p: DayTwoPlayer) -> list[str]:
    return checks.b4_relative(p, day2("babysitter", p.seed)) if name in TOOL_USERS else []


CHECKS: dict[str, Callable[[str, DayTwoPlayer], list[str]]] = {
    "story_order": lambda _, p: checks.story_order(p.landed_at),
    "b4_relative": _relative,
}


@cache
def verdicts(name: str, seed: int = 0) -> dict[str, list[str]]:
    p = day2(name, seed)
    return {check: run(name, p) for check, run in CHECKS.items()}
