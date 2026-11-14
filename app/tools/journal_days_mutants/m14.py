"""Row 14 of tests/saves/MUTANTS_journal_days.txt: a PUT's newest_day_read replaces the kept one, lower or null."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/accounts/presentation.py',
     '        elif field in HIGHEST:\n',
     '        elif False:\n'),
]
