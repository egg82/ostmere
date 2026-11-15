"""Row 09 of tests/saves/MUTANTS_journal_days.txt: Opened carries blank and gap days too."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'return tuple(d for d in stored if d.notes)\n',
     'return tuple(stored)\n'),
    ('ashfall_app/saves/journal_write.py',
     'for d in stored if d.notes)\n',
     'for d in stored)\n'),
]
