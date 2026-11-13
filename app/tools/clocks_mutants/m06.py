"""Row 06 of tests/db/MUTANTS_clocks.txt: the prune deletes the doomed accounts without judging their progress again."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/accounts.py',
     'accounts.c.id.in_(doomed), ~progress)).rowcount',
     'accounts.c.id.in_(doomed))).rowcount'),
]
