"""Row 40 of MUTANTS.txt: chained not served."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/convert.py',
     'lost=f.lost, chained=f.chained)',
     'lost=f.lost, chained=0)'),
]
