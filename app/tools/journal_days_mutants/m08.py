"""Row 08 of tests/saves/journal/MUTANTS_journal_days.txt: the day the step stops in is composed as ended, its end written before it
ends."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'ended=time >= end, losses',
     'ended=True, losses'),
]
