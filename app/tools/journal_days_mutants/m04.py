"""Row 04 of tests/saves/MUTANTS_journal_days.txt: the locking read reads lines of the day not yet ended."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/journal.py',
     '        ln.at < ended * DAY_S).scalar_subquery()\n',
     '        ln.at < (ended + 1) * DAY_S).scalar_subquery()\n'),
]
