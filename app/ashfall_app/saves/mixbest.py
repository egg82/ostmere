"""The player's own earlier best per goal (api/contract/mix-rows.txt, "Mix rows"): when a mix is saved, when each open goal
would land under it at the rates as set then, kept per goal with the mix that set it. A goal is kept as the api's goal
key (an opaque string here); a later save replaces a goal's entry only with a strictly earlier landing, so a tie stays
with the earlier mix. Kept on the save's row; a mix edited or deleted later does not change what it set."""

from dataclasses import dataclass

from .. import engine as e
from ..engine.codec import Json


@dataclass(frozen=True)
class Best:
    goal: str
    mix: str
    lands_at: int
    """The game time the goal would land, as projected when `mix` was saved."""
    at: int
    """The game time `mix` was saved."""


def merged(kept: tuple[Best, ...], mix: e.MixId, at: int, marks: tuple[tuple[str, int], ...]) -> tuple[Best, ...]:
    """`kept` with each goal `mix` lands at the time `marks` gives, when that is earlier than the kept one."""
    by_goal = {b.goal: b for b in kept}
    for goal, landed in marks:
        old = by_goal.get(goal)
        if old is None or landed < old.lands_at:
            by_goal[goal] = Best(goal, str(mix), landed, at)
    return tuple(by_goal.values())


def to_json(kept: tuple[Best, ...]) -> Json:
    return [[b.goal, b.mix, b.lands_at, b.at] for b in kept]


def from_json(value: Json) -> tuple[Best, ...]:
    """What to_json wrote; () for None or anything else."""
    if not isinstance(value, list):
        return ()
    out: list[Best] = []
    for item in value:
        if (isinstance(item, list) and len(item) == 4 and isinstance(item[0], str) and isinstance(item[1], str)
                and isinstance(item[2], int) and isinstance(item[3], int)):
            out.append(Best(item[0], item[1], item[2], item[3]))
    return tuple(out)
