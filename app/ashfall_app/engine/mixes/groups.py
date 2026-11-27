"""A group's crew at run time: who is in a pooled lane, who of them is free, and a group card's share times its crew
(design/groups.txt, "GROUPS (pooled lanes)", "How a group's split runs"). mixruns._town_entries is the one reader."""
from dataclasses import dataclass

from ..people.gone import is_left
from ..core.ids import CardId, LaneId
from ..core.index import index
from .mixes import CardShare, SpentShare
from ..modifiers.modifiers import Run, RunKind
from ..core.rules import Rules
from ..core.state import Save
from ..unlocks.unlocked import is_unlocked
from ..unlocks.unlocks import Unlock, UnlockKind

type Entries = tuple[tuple[CardId, int, Run], ...]
type Gains = dict[CardId, tuple[SpentShare, ...]]


@dataclass(frozen=True)
class Crew:
    """The people of one group now: the unmarked, joined, present members, and those of them holding no tap."""

    members: frozenset[LaneId]
    free: int


def _joined(save: Save, rules: Rules, lane: LaneId) -> bool:
    return is_unlocked(save, rules, Unlock(UnlockKind.JOINED, lane))


def crews(save: Save, rules: Rules) -> dict[LaneId, Crew]:
    """Each pooled lane with at least one member now."""
    busy = {ls.lane for ls in save.lanes if ls.card is not None}
    unmarked = {ls.lane for ls in save.lanes if not ls.own_split}
    found: dict[LaneId, set[LaneId]] = {}
    for d in rules.lanes:
        if d.group is not None and d.id in unmarked and _joined(save, rules, d.id) and not is_left(save, d.id):
            found.setdefault(d.group, set()).add(d.id)
    return {g: Crew(frozenset(m), len(m - busy)) for g, m in found.items()}


def group_crew(save: Save, rules: Rules, lane: LaneId) -> int | None:
    """The free members of pooled lane `lane` (0 with none), None for a lane that is no group."""
    if lane not in index(rules).pooled:
        return None
    found = crews(save, rules).get(lane)
    return 0 if found is None else found.free


def present(save: Save, rules: Rules, shares: tuple[CardShare, ...]) -> tuple[CardShare, ...]:
    """The shares that run: a card of a pooled lane with members, of a joined person who runs their own split; an
    unmarked person's own shares idle in the mix, kept."""
    found = crews(save, rules)
    cards = index(rules).cards
    pooled = index(rules).pooled
    members = frozenset(m for c in found.values() for m in c.members)
    return tuple(s for s in shares
                 if (cards[s.card].lane in found if cards[s.card].lane in pooled
                     else cards[s.card].lane not in members and _joined(save, rules, cards[s.card].lane)))


def crewed(save: Save, rules: Rules, entries: Entries, gains: Gains) -> tuple[Entries, Gains]:
    """The entries with each group card's share, and what it gains, times the free members: none free leaves the
    share and a full run YIELDED."""
    found = crews(save, rules)
    if not found:
        return entries, gains
    cards = index(rules).cards
    free = {c: found[cards[c].lane].free for c, _, _ in entries if cards[c].lane in found}
    return (tuple(_crewed_entry(e, free.get(e[0])) for e in entries),
            {c: tuple(SpentShare(g.card, g.share_bp * free[c]) for g in got) if free.get(c) else got
             for c, got in gains.items()})


def _crewed_entry(entry: tuple[CardId, int, Run], free: int | None) -> tuple[CardId, int, Run]:
    card, share, run = entry
    if free is None:
        return entry
    if free:
        return card, share * free, run
    return card, share, Run(RunKind.YIELDED, 0, 1) if run.kind is RunKind.FULL else run
