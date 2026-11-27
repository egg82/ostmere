"""What a Mark does to a save: a joined person's mark is set or cleared, and never a share removed. Semantics:
design/groups.txt, "GROUPS (pooled lanes)", "Mark"."""
from dataclasses import replace

from .cards import Mark
from .gone import is_left
from .ids import LaneId, MixId
from .joins import is_joined, with_share
from .rules import Rules
from .state import Save


def marked(save: Save, rules: Rules, marks: tuple[Mark, ...]) -> Save:
    """Each mark in tuple order, unless its lane has not joined or has left (then it changes nothing). Setting the mark
    gives the person the mark's card as a whole share when the town mix holds none of theirs; clearing it does the same
    for the group, the card being one on the group, as an unmarked join's is."""
    for m in marks:
        if is_joined(save, rules, m.lane) and not is_left(save, m.lane):
            save = replace(save, lanes=tuple(replace(ls, own_split=m.own_split) if ls.lane == m.lane else ls
                                             for ls in save.lanes))
            mix = _town_mix(rules, m.lane)
            if mix is not None:
                save = with_share(save, rules, m.lane if m.own_split else _group(rules, m.lane), mix, m.card)
    return save


def _group(rules: Rules, lane: LaneId) -> LaneId | None:
    return next((d.group for d in rules.lanes if d.id == lane), None)


def _town_mix(rules: Rules, lane: LaneId) -> MixId | None:
    """The mix the lane's person joined into."""
    outcomes = [*(t.outcome for t in rules.triggers), *(a.outcome for o in rules.offers for a in o.answers)]
    return next((j.mix for o in outcomes for j in o.joins if j.lane == lane), None)
