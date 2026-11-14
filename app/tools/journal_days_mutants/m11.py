"""Row 11 of tests/saves/MUTANTS_journal_days.txt: the composed days are not stored."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/write.py',
     '[journal_write.stored_form(d) for d in days])',
     '[])'),
]
