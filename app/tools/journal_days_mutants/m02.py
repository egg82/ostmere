"""Row 02 of tests/saves/MUTANTS_journal_days.txt: the locking read always says its snapshot is fresh."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/journal.py',
     'return [next_day.label("j_next"), fresh.label("j_fresh")',
     'return [next_day.label("j_next"), (next_day == next_day).label("j_fresh")'),
]
