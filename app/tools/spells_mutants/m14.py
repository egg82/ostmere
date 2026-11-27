"""Row 14 of MUTANTS.txt: links move lost."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     '    save, lines = apply_outcome(save, rules, Outcome(stores=(Amount(fight.chained, k * QUANTITY_SCALE),), lines=links))\n',
     '    save, lines = apply_outcome(save, rules, Outcome(stores=(Amount(fight.chained, k * QUANTITY_SCALE), Amount(fight.lost, k * QUANTITY_SCALE)), lines=links))\n'),
]
