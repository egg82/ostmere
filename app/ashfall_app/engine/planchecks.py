"""What makes an outcome's take-aways from the player's plan valid: retired chores and leaves (DESIGN.txt, "Retired
chores", "Validation"; "LEAVES", invariant 155). rules_check calls it for every outcome."""
from typing import TYPE_CHECKING

from .cards import Outcome
from .errors import InvalidRulesError
from .leaveparts import all_leaves

if TYPE_CHECKING:
    from .rules import Rules


def check_retire(rules: "Rules", o: Outcome, where: str, trigger: bool) -> None:
    """retire_orders only in a trigger's outcome (`trigger`), each a declared card, none named twice."""
    cards = {c.id for c in rules.cards}
    seen: set[str] = set()
    for c in o.retire_orders:
        if not trigger:
            raise InvalidRulesError(f"{where}: only a trigger's outcome retires orders ({c})")
        if c not in cards:
            raise InvalidRulesError(f"{where}: retires the orders on an unknown card {c}")
        if c in seen:
            raise InvalidRulesError(f"{where}: retires the orders on {c} twice")
        seen.add(c)


def check_leaves(rules: "Rules", o: Outcome, where: str, once_only: bool) -> None:
    """Leaves only in a trigger's or an answer's outcome (`once_only`), each of a declared ruled lane, each stop a
    declared standing action."""
    ruled = {d.id for d in rules.lanes if d.ruled}
    standing = {a.id for a in rules.standing}
    for leave in o.leaves:
        if not once_only:
            raise InvalidRulesError(f"{where}: only a trigger's or an answer's outcome has a person leave ({leave.lane})")
        if leave.lane not in ruled:
            raise InvalidRulesError(f"{where}: leaves {leave.lane}, which is not a declared ruled lane")
        unknown = [a for a in leave.stops if a not in standing]
        if unknown:
            raise InvalidRulesError(f"{where}: leaves {leave.lane}, stopping {unknown[0]}, which is not a standing action")


def check_one_leave_each(rules: "Rules") -> None:
    """At most one Leave per lane across every outcome of the rules: a leave's stops are read off the rules."""
    seen: set[str] = set()
    for leave in all_leaves(rules):
        if leave.lane in seen:
            raise InvalidRulesError(f"lane {leave.lane}: left by two outcomes")
        seen.add(leave.lane)
