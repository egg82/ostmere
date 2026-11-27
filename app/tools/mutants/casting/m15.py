"""Row 15 of MUTANTS.txt: role check."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/cast_checks.py',
     '        if ROLE.fullmatch(c.role) is None:\n',
     '        if False:\n'),
]
