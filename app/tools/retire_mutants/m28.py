"""Row 28 of MUTANTS_leaves.txt, m28: validation: a card named twice is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/planchecks.py',
     '        if c in seen:\n',
     '        if False:\n'),
]
