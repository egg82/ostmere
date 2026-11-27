"""What makes pooled lanes, groups, marks and unmarked joins valid (design/groups.txt, "GROUPS (pooled lanes)", "Validation").
rules_check calls it for the lanes and for every outcome."""
from typing import TYPE_CHECKING

from ..cards.cards import Join, Mark, Outcome
from ..core.errors import InvalidRulesError
from ..core.ids import TOWN_PREFIX, CardId

if TYPE_CHECKING:
    from ..core.rules import Rules


def check_groups(rules: "Rules") -> None:
    """A pooled lane is ruled, has no group and holds uncapped cards only; a group names a pooled lane, and only a
    ruled lane has one."""
    pooled = {d.id for d in rules.lanes if d.pooled}
    for d in rules.lanes:
        if d.pooled and not d.ruled:
            raise InvalidRulesError(f"lane {d.id}: a pooled lane is a ruled lane")
        if d.group is None:
            continue
        if d.pooled:
            raise InvalidRulesError(f"lane {d.id}: a pooled lane has no group")
        if not d.ruled:
            raise InvalidRulesError(f"lane {d.id}: only a ruled lane has a group")
        if d.group not in pooled:
            raise InvalidRulesError(f"lane {d.id}: group {d.group} is not a pooled lane")
    for c in rules.cards:
        if c.lane in pooled and c.cap is not None:
            raise InvalidRulesError(f"card {c.id}: a card on a pooled lane has no cap")


def check_group_outcome(rules: "Rules", o: Outcome, where: str, once_only: bool) -> None:
    """In any outcome: no start, install or queue taps a pooled lane's card. In a trigger's or an answer's (`once_only`)
    alone: marks, each of a declared person's lane, its card an uncapped one on that lane (on its group for an unmarking), an unmarking only for a
    lane with a group."""
    pooled_cards = _pooled_cards(rules)
    for card in (*o.starts, *(i.card for i in o.orders), *o.queues):
        if card in pooled_cards:
            raise InvalidRulesError(f"{where}: taps {card}, a card on a pooled lane")
    for m in o.marks:
        if not once_only:
            raise InvalidRulesError(f"{where}: only a trigger's or an answer's outcome marks a person ({m.lane})")
        _check_mark(rules, m, where)
    for leave in o.leaves:
        if leave.lane in {d.id for d in rules.lanes if d.pooled}:
            raise InvalidRulesError(f"{where}: leaves {leave.lane}, a pooled lane, which is never a person")


def join_problem(rules: "Rules", j: Join) -> str | None:
    """Why `j` cannot be a join, or None: its lane is a declared ruled lane that is no pooled lane, its mix id a town
    one, its card (if any) an uncapped card on that lane, or on the lane's group when the join is unmarked, which needs
    one (engine/design/, "THE TOWN'S MIX", invariant 96; "GROUPS (pooled lanes)")."""
    lanes = {d.id: d for d in rules.lanes}
    if j.lane not in lanes or not lanes[j.lane].ruled or lanes[j.lane].pooled:
        return "lane is not a declared ruled lane that is a person"
    if not j.mix.startswith(TOWN_PREFIX):
        return f"mix does not begin {TOWN_PREFIX!r}"
    group = lanes[j.lane].group
    if not j.own_split and group is None:
        return "an unmarked join's lane has no group"
    capped = {c.id for c in rules.cards if c.cap is not None}
    on_lane = {c.id for c in rules.cards if c.lane == (j.lane if j.own_split else group)}
    return None if j.card is None or (j.card in on_lane and j.card not in capped) else "card is not an uncapped card on the lane or group"


def _check_mark(rules: "Rules", m: Mark, where: str) -> None:
    people = {d.id for d in rules.lanes if d.ruled and not d.pooled}
    if m.lane not in people:
        raise InvalidRulesError(f"{where}: marks {m.lane}, which is not a declared person's lane")
    if not m.own_split and _group_of(rules, m.lane) is None:
        raise InvalidRulesError(f"{where}: unmarks {m.lane}, which has no group")
    capped = {c.id for c in rules.cards if c.cap is not None}
    home = m.lane if m.own_split else _group_of(rules, m.lane)
    on_lane = {c.id for c in rules.cards if c.lane == home}
    if m.card is not None and (m.card not in on_lane or m.card in capped):
        raise InvalidRulesError(f"{where}: marks {m.lane} with {m.card}, which is not an uncapped card on "
                                f"{'the lane' if m.own_split else 'its group'}")


def _pooled_cards(rules: "Rules") -> set[CardId]:
    pooled = {d.id for d in rules.lanes if d.pooled}
    return {c.id for c in rules.cards if c.lane in pooled}


def _group_of(rules: "Rules", lane: str) -> str | None:
    return next((d.group for d in rules.lanes if d.id == lane), None)
