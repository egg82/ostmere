"""Row 13 of MUTANTS.txt: links count as fought."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     '    save, lines = apply_outcome(save, rules, Outcome(stores=(Amount(fight.chained, k * QUANTITY_SCALE),), lines=links))\n',
     '    save, lines = apply_outcome(save, rules, Outcome(stores=(Amount(fight.chained, k * QUANTITY_SCALE), Amount(fight.fought, k * QUANTITY_SCALE)), lines=links))\n'),
]
