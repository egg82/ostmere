"""Row 16 of MUTANTS.txt: role twice."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/cast_checks.py',
     '        if c.role in named:\n',
     '        if False:\n'),
]
