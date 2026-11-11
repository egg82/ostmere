"""Row 19 of MUTANTS_held.txt: validation accepts an amount_bp of 0 or less."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/fightcheck.py',
     '_require(w.amount_bp >= 1,',
     '_require(w.amount_bp >= -10**9,'),
]
