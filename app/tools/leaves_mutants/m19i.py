"""Row 19 of MUTANTS_leaves.txt, m19i: loader: a join of the lane in the outcome that leaves it is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/leave_checks.py',
     '            if leave.lane in joined:\n',
     '            if False:\n'),
]
