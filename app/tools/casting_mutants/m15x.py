"""Row 15 of MUTANTS.txt: lane or slot."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/cast_checks.py',
     '        if c.role in lanes or c.role in fixed_slots():\n',
     '        if False:\n'),
]
