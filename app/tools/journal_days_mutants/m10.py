"""Row 10 of tests/saves/MUTANTS_journal_days.txt: a day closed, or stored whole, is appended to like one still being
written."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/step.py',
     '        where=and_(t.through.is_not(None), t.through < (t.day + 1) * DAY_S),\n',
     ''),
]
