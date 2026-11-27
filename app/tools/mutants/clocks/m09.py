"""Row 09 of tests/db/MUTANTS_clocks.txt: a 410 is an error, not a gone subscription."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/reminders/sender.py',
     'if status in (404, 410):',
     'if status in (404,):'),
]
