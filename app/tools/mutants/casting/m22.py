"""Row 22 of MUTANTS.txt: unknown feature."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/rules/casts.py',
     '    lanes = candidates(o)\n    return {c.role:',
     '    lanes = [x.id for x in o.lanes]\n    return {c.role:'),
]
