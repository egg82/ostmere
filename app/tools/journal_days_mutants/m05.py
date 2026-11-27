"""Row 05 of tests/saves/journal/MUTANTS_journal_days.txt: the step's own lines, not yet stored, are left out of the days it
closes."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     '[*keyed, *((ln.time, str(ln.key)) for ln in lines)]',
     '[*keyed]'),
]
