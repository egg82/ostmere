"""Row 19 of MUTANTS_leaves.txt, m19d: validation: an undeclared stop is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/planchecks.py',
     '        if unknown:\n',
     '        if False:\n'),
]
