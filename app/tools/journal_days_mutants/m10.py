"""Row 10 of tests/saves/MUTANTS_journal_days.txt: a day the save already holds fails the step's write instead of being
left as stored."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/step.py',
     '.on_conflict_do_nothing(index_elements=["save_id", "day"]).returning(save_journal.c.day)',
     '.returning(save_journal.c.day)'),
]
