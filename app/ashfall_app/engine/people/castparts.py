"""Every Cast part the rules hold, read by validation (castchecks), the unlock ids the rules know (unlock_known) and the
casts themselves (casts). Reads the rules alone, imported below rules.py, so it names Rules for type checking only."""
from typing import TYPE_CHECKING

from ..cards.cards import Cast
from ..core.derived import derived
from ..core.ids import FeatureId, LaneId

if TYPE_CHECKING:
    from ..core.rules import Rules


def all_casts(rules: "Rules") -> tuple[Cast, ...]:
    """The Cast parts of every outcome: cards', triggers' and answers' (validation allows the last two only)."""
    outcomes = [o for c in rules.cards for o in (c.outcome, c.finished)] + [t.outcome for t in rules.triggers]
    outcomes += [a.outcome for x in rules.offers for a in x.answers]
    return tuple(c for o in outcomes for c in o.casts)


def cast_features(rules: "Rules") -> dict[LaneId, frozenset[FeatureId]]:
    """Each lane's features a cast of any role may give it."""
    return derived(rules, "_cast_features", _features)


def _features(rules: "Rules") -> dict[LaneId, frozenset[FeatureId]]:
    found: dict[LaneId, set[FeatureId]] = {}
    for c in all_casts(rules):
        for p in c.picks:
            found.setdefault(p.lane, set()).add(p.feature)
    return {lane: frozenset(f) for lane, f in found.items()}
