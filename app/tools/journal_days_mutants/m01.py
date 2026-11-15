"""Row 01 of tests/saves/MUTANTS_journal_days.txt: a locking read that waited on another write is trusted, so a step
that waited on the save's row recomposes from what it read before the first stored."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     '    if seen.fresh:\n',
     '    if True:\n'),
]
