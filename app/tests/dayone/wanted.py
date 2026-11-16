"""The stores something in the rules wants (the cap-loss check's narrowing, capcheck.py): a card takes it (an input, a
cost, a drain, or what a lost fight takes), a standing action takes it (a cost or what a lost fight takes), or a
condition reads it (a card's requires, a chip's or a trigger's when). A store only made, or only raised in cap, is not
wanted. Read from the rules' structure alone: store ids, never names or words (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import AfterTime, Condition, Rules, StoreValue
from ashfall_app.engine.cardsides import card_costs
from ashfall_app.engine.fightlines import fight_costs


def read_by(cond: Condition) -> frozenset[str]:
    """The store a condition reads, none when it reads time or anything but a store."""
    if isinstance(cond, AfterTime) or not isinstance(cond.subject, StoreValue):
        return frozenset()
    return frozenset((str(cond.subject.store),))


def wanted(rules: Rules) -> frozenset[str]:
    taken = {str(s) for c in rules.cards for s in card_costs(c)}
    taken |= {str(f.store) for a in rules.standing for f in a.costs}
    taken |= {str(x.store) for a in rules.standing if a.fight for x in fight_costs(a.fight)}
    conds = [r for c in rules.cards for r in c.requires] + [c.when for c in rules.chips] + [t.when for t in rules.triggers]
    return frozenset(taken).union(*(read_by(c) for c in conds))
