"""Row 20 of MUTANTS.txt: slot anywhere."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/cast_checks.py',
     '            if slot in roles and (where, key) not in allowed[slot]:\n',
     '            if False:\n'),
]
