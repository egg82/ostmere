"""Row 04 of tests/saves/journal/MUTANTS_journal_days.txt: lines stored past the step's save time are composed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     '    history = history[:bisect_right([ln.at for ln in history], time)]\n',
     ''),
]
