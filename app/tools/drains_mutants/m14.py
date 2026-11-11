"""Row 14 of MUTANTS_drains.txt: cure_reading.takes ignores drains."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/cure_reading.py',
     'for a in (*card.inputs, *card.drains)), *(str(f.store)',
     'for a in card.inputs), *(str(f.store)'),
]
