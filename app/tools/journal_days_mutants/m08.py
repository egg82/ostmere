"""Row 08 of tests/saves/MUTANTS_journal_days.txt: the day the step stops in is composed before it ends."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     '    j, closed = rs.journal, time // DAY_S\n',
     '    j, closed = rs.journal, time // DAY_S + 1\n'),
]
