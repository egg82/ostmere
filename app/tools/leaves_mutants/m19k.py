"""Row 19 of MUTANTS_leaves.txt, m19k: loader: a leave outside a trigger's or an answer's outcome is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/leave_checks.py',
     '        if out.leaves and where not in once:\n',
     '        if False:\n'),
]
