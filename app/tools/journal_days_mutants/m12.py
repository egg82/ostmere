"""Row 12 of tests/saves/journal/MUTANTS_journal_days.txt: a day not written is served."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/service.py',
     'for d in days if d.notes]',
     'for d in days]'),
]
