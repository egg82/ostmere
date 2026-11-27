"""Row 09 of tests/saves/journal/MUTANTS_journal_days.txt: Opened carries blank and gap days too."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'return tuple(d for d in map(day_of, found) if d.notes)\n',
     'return tuple(map(day_of, found))\n'),
]
