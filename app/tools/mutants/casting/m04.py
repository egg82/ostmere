"""Row 04 of MUTANTS.txt: recast."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/casts.py',
     '        if not any(p.feature in held for p in c.picks):\n',
     '        if True:\n'),
]
