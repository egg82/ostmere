"""The stores something in the rules wants (the cap-loss check's narrowing, capcheck.py): a card spends it (an input, a
cost or a drain), a standing action spends it (a cost), or a condition reads it (a card's requires, a chip's or a
trigger's when). A store only made, only raised in cap, or only taken by a lost fight (a raid is a loss, not a use) is
not wanted. Read from the rules' structure alone: store ids, never names or words (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import AfterTime, Condition, Rules, StoreValue


def read_by(cond: Condition) -> frozenset[str]:
    """The store a condition reads, none when it reads time or anything but a store."""
    if isinstance(cond, AfterTime) or not isinstance(cond.subject, StoreValue):
        return frozenset()
    return frozenset((str(cond.subject.store),))


def wanted(rules: Rules) -> frozenset[str]:
    taken = {str(f.store) for c in rules.cards for f in c.costs} | {str(f.store) for a in rules.standing for f in a.costs}
    taken |= {str(x.store) for c in rules.cards for x in (*c.inputs, *c.drains)}
    conds = [r for c in rules.cards for r in c.requires] + [c.when for c in rules.chips] + [t.when for t in rules.triggers]
    return frozenset(taken).union(*(read_by(c) for c in conds))
