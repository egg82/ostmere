"""Row 15 of MUTANTS.txt: tally not by k."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     'Amount(fight.chained, k * QUANTITY_SCALE)',
     'Amount(fight.chained, QUANTITY_SCALE)'),
]
