"""Row 03 of tests/saves/MUTANTS_journal_days.txt: the locking read reads the days only once two days are due."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/journal.py',
     '    due = next_day < ended\n',
     '    due = next_day < ended - 1\n'),
]
