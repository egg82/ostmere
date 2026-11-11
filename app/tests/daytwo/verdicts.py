"""Each of day two's invariant checks on a played route (docs/design/sim-invariants.md): its beats all land in order, a
tool user's B4 lags the babysitter's only by its own gaps, and away from day two's end no gathered store loses over
half its making to its cap on the typical route. The route's rhythm is its readout (report.py)."""
from collections.abc import Callable
from functools import cache

from tests.daythree.routes import day3
from tests.daytwo import caps, checks
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import day2
from tests.dayone import capcheck
from tests.dayone.routes import TOOL_USERS


def _relative(name: str, p: DayTwoPlayer) -> list[str]:
    return checks.b4_relative(p, day2("babysitter", p.seed)) if name in TOOL_USERS else []


def _cap_loss(name: str, p: DayTwoPlayer) -> list[str]:
    """Away from day two's end as a player has it: the chapters after it merged, so the sinks the page offers from B4
    on are there (caps.shipped_end)."""
    return capcheck.problems(caps.shipped_cap_loss_failing(day3(name, p.seed))) if name == "typical" else []


CHECKS: dict[str, Callable[[str, DayTwoPlayer], list[str]]] = {
    "story_order": lambda _, p: checks.story_order(p.landed_at),
    "b4_relative": _relative,
    "cap_loss": _cap_loss,
}


@cache
def verdicts(name: str, seed: int = 0) -> dict[str, list[str]]:
    p = day2(name, seed)
    return {check: run(name, p) for check, run in CHECKS.items()}
