"""Row 30 of MUTANTS_leaves.txt, m30: digest moves: the rules encoding writes `retire_orders` for every outcome."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '("Outcome", "joins"), ("Outcome", "retire_orders"),',
     '("Outcome", "joins"),'),
]
RELOCK = True
