"""Row 05 of tests/db/MUTANTS_clocks.txt: the prune deletes the doomed accounts' saves without judging their decisions again."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/accounts.py',
     'saves.c.account_id.in_(doomed), saves.c.decisions == 0))',
     'saves.c.account_id.in_(doomed)))'),
]
