"""Row 19 of MUTANTS_leaves.txt, m19g: loader: a Leave of a lane that is not ruled is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/leave_checks.py',
     '            if leave.lane not in ruled:\n',
     '            if False:\n'),
]
