"""Row 15 of MUTANTS_drains.txt: a drain card may repeat."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/retap.py',
     ' and not card.drains and not card.lines',
     ' and not card.lines'),
]
