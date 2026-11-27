"""Who has left the town, read off the unlock set (Unlock(LEFT, lane)), and the standing actions their leaving stopped,
read off the rules' Leave parts. Derived, never stored; a leaf below counts and rates, which both read it (design/leaves.txt,
"LEAVES")."""
from ..core.ids import ActionId, CardId, LaneId
from ..core.index import derived
from .leaveparts import all_leaves
from ..core.memo import PartsMemo
from ..core.rules import Rules
from ..core.state import Save
from ..unlocks.unlocks import UnlockKind

_LEFT: PartsMemo[frozenset[str]] = PartsMemo()
"""Kept while the save's unlock set is the same tuple."""


def left_lanes(save: Save) -> frozenset[str]:
    """The lanes whose person has left."""
    return _LEFT.get((save.unlocked,), lambda: frozenset(u.id for u in save.unlocked if u.kind is UnlockKind.LEFT))


def is_left(save: Save, lane: LaneId) -> bool:
    return lane in left_lanes(save)


def left_cards(save: Save, rules: Rules) -> frozenset[CardId]:
    """The cards on a lane whose person has left: out of play for good."""
    gone = left_lanes(save)
    return frozenset(c.id for c in rules.cards if c.lane in gone) if gone else frozenset()


def stopped(save: Save, rules: Rules) -> frozenset[ActionId]:
    """The standing actions named in the stops of a Leave whose lane has left."""
    gone = left_lanes(save)
    if not gone:
        return frozenset()
    stops = derived(rules, "_leave_stops", _stops)
    return frozenset(a for lane in gone for a in stops.get(LaneId(lane), ()))


def _stops(rules: Rules) -> dict[LaneId, tuple[ActionId, ...]]:
    """Each Leave's stops by its lane (validation allows one Leave per lane)."""
    found: dict[LaneId, tuple[ActionId, ...]] = {}
    for leave in all_leaves(rules):
        found[leave.lane] = found.get(leave.lane, ()) + leave.stops
    return found
