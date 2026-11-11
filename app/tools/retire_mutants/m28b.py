"""Row 28 of MUTANTS_leaves.txt, m28b: validation: an undeclared card is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/planchecks.py',
     '        if c not in cards:\n',
     '        if False:\n'),
]
