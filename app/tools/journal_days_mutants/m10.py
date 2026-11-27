"""Row 10 of tests/saves/journal/MUTANTS_journal_days.txt: a day closed is appended to like one still being written."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/stored/step.py',
     '        where=t.through < (t.day + 1) * DAY_S,\n',
     ''),
]
