"""Row 19 of MUTANTS_leaves.txt, m19b: validation: a Leave of an undeclared or non-ruled lane is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/planchecks.py',
     '        if leave.lane not in ruled:\n',
     '        if False:\n'),
]
