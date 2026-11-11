"""Row 28 of MUTANTS_leaves.txt, m28c: validation: retire_orders in an answer's or a card's outcome is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/planchecks.py',
     '        if not trigger:\n',
     '        if False:\n'),
]
