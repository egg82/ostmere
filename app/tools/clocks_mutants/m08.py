"""Row 08 of tests/db/MUTANTS_clocks.txt: the sender follows redirects."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/reminders/sender.py',
     'session.max_redirects = 0',
     'session.max_redirects = 5'),
]
