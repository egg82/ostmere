"""Row 18 of MUTANTS_leaves.txt, m18: digest moves: the rules encoding writes `leaves` for every outcome."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '("Outcome", "retire_orders"), ("Outcome", "leaves"),\n',
     '("Outcome", "retire_orders"),\n'),
]
RELOCK = True
