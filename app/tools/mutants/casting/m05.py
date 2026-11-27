"""Row 05 of MUTANTS.txt: slot any outcome."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/checks/people/cast_checks.py',
     '        if any(c.role == role for c in outcome.casts):\n',
     '        if True:\n'),
]
