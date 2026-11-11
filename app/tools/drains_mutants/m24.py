"""Row 24 of MUTANTS_drains.txt: a fight card's loss odds scale its drain."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/odds.py',
     '            found.append((c.id, c.fight, wins, _losses(c.id, c.fight)))\n',
     '            found.append((c.id, c.fight, wins, _losses(c.id, c.fight)\n                          + tuple(RateRef(c.id, FlowKind.COST, a.store) for a in c.drains)))\n'),
]
