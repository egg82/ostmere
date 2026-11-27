"""Row 22 of MUTANTS_spent.txt: a standing action is no maker."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     '    for a in rules.standing:\n',
     '    for a in ():\n'),
]
