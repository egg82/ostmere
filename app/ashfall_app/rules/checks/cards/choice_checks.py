"""The check that no lane offers a job another job on it beats outright (game-design: a dominated option is a
non-choice). On one lane, card A beats card B when A pays at least B's every lump, flow and XP, takes at most B's every
input, drain and cost, waits on no condition B does not, and takes no longer. B is never worth choosing then, unless
an outcome retires it in A's favour (`replaced_by`, as the hands' gathering gives way to woodcutting). Structural
fields only, never ids or words.

Only jobs are compared: uncapped cards that make a store and whose completion does nothing else. A capped card is a
step, and a card that makes nothing, holds a fight or a while-running entry, does more on completion than pay stores,
or has its completion count read by a condition pays something the stores cannot show. Raises ValueError naming the
pair (refs.fail)."""
from collections import defaultdict
from typing import TYPE_CHECKING

from ...entries.entries import OutcomeEntry
from ...refs import conditions, fail, outcomes

if TYPE_CHECKING:
    from ...entries.entries import CardEntry, FlowEntry, ItemAmount
    from ...schema import Opening

_NOTHING = OutcomeEntry()


def check_choices(o: "Opening") -> None:
    for beater, beaten in beaten_pairs(o):
        fail(f"card {beaten.id}", f"is beaten outright by {beater.id} on lane {beaten.lane}: at least the same outcome, "
             "at least as fast, with no extra input, requirement or skill cost; retire it in that card's favour "
             "(replaced_by) or make it pay something the other does not")


def beaten_pairs(o: "Opening") -> list[tuple["CardEntry", "CardEntry"]]:
    """(beater, beaten) for each pair that check_choices refuses."""
    replaced = {(u.id, u.replaced_by) for _, out in outcomes(o) for u in out.unlocks if u.unlock_kind == "retired"}
    profiles = {id(c): _Profile(c) for c in o.cards}
    return [(a, b) for a, b in compared_pairs(o)
            if _beats(profiles[id(a)], profiles[id(b)]) and (b.id, a.id) not in replaced]


def compared_pairs(o: "Opening") -> list[tuple["CardEntry", "CardEntry"]]:
    """Every ordered pair of distinct jobs sharing a lane."""
    counted = {c.id for _, c, _ in conditions(o) if c.subject_kind == "card_count"}
    by_lane: dict[str, list["CardEntry"]] = defaultdict(list)
    for c in o.cards:
        if c.id not in counted and _job(c):
            by_lane[c.lane].append(c)
    return [(a, b) for cards in by_lane.values() for a in cards for b in cards if a is not b]


class _Profile:
    """What `beats` reads of a card, summed once so a pair costs only the comparison."""

    def __init__(self, c: "CardEntry") -> None:
        self.card = c
        self.lumps = _lumps(c.outcome.stores)
        self.makes = _flows(c.makes)
        self.inputs = _lumps(c.inputs)
        self.drains = _lumps(c.drains)
        self.costs = _flows(c.costs)


def beats(a: "CardEntry", b: "CardEntry") -> bool:
    return _beats(_Profile(a), _Profile(b))


def _beats(pa: _Profile, pb: _Profile) -> bool:
    a, b = pa.card, pb.card
    return (a.work_s <= b.work_s
            and _at_least(pa.lumps, pb.lumps)
            and _at_least(pa.makes, pb.makes)
            and (b.xp_per_hour == 0 or (a.skill == b.skill and a.xp_per_hour >= b.xp_per_hour))
            and _at_least(pb.inputs, pa.inputs)
            and _at_least(pb.drains, pa.drains)
            and _at_least(pb.costs, pa.costs)
            and all(r in b.requires for r in a.requires))


def _job(c: "CardEntry") -> bool:
    return (c.cap is None and bool(c.outcome.stores or c.makes) and c.fight is None and not c.while_running
            and c.outcome.model_copy(update={"stores": [], "line_keys": []}) == _NOTHING
            and c.finished.model_copy(update={"line_keys": []}) == _NOTHING)


def _at_least(more: dict[str, float], less: dict[str, float]) -> bool:
    """`more` holds every store of `less`, each by at least as much."""
    return all(more.get(store, 0) >= amount for store, amount in less.items())


def _lumps(amounts: "list[ItemAmount]") -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for a in amounts:
        out[a.store] += a.items / a.every
    return out


def _flows(flows: "list[FlowEntry]") -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for f in flows:
        out[f.store] += f.items_per_hour / f.every_hours
    return out
