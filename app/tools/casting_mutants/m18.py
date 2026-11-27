"""Row 18 of MUTANTS.txt: twice."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/cast_checks.py',
     '            if pattern in c.patterns[:i]:\n',
     '            if False:\n'),
]
