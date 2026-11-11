"""Row 32 of MUTANTS_leaves.txt, m32: loader anywhere: retire_orders on a trigger that is not a season's turn, or on a card, is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/retire_checks.py',
     '        if where not in seasons:\n',
     '        if False:\n'),
]
