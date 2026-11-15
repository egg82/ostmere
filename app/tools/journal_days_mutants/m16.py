"""Row 16 of tests/saves/MUTANTS_journal_days.txt: a day written as it went is put in the old page order when read, as a
day stored whole is."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'for d, r in zip(stored, found) if r.through is None)',
     'for d, r in zip(stored, found))'),
    ('ashfall_app/saves/journal_write.py',
     'if r.through is None else d\n',
     'if True else d\n'),
]
