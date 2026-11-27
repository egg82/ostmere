"""Row 19 of MUTANTS_leaves.txt, m19j: loader: a stop that is not a standing action is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/leave_checks.py',
     '                if a not in standing:\n',
     '                if False:\n'),
]
