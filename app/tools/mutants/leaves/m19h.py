"""Row 19 of MUTANTS_leaves.txt, m19h: loader: a lane left by two outcomes is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/leave_checks.py',
     '            if leave.lane in left:\n',
     '            if False:\n'),
]
