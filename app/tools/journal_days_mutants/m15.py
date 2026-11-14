"""Row 15 of tests/saves/MUTANTS_journal_days.txt: Opened carries no stored day."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/service.py',
     '            days = journal_write.written(conn, save_id)\n',
     '            days = ()\n'),
]
