"""Row 09 of tests/saves/MUTANTS_journal_days.txt: Opened carries blank and gap days too."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'if (d := day_of(r)).notes)',
     'if (d := day_of(r)))'),
]
