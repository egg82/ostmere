"""Row 02 of tests/saves/journal/MUTANTS_journal_days.txt: the locking read always says its snapshot is fresh."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/journal.py',
     'return [fresh.label("j_fresh")',
     'return [literal_column("true").label("j_fresh")'),
]
