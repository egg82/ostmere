"""Row 03 of tests/saves/journal/MUTANTS_journal_days.txt: a day still being written has its stored notes replaced by what the step
adds, not appended to."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/stored/step.py',
     '"notes": t.notes.op("||")(new.notes)',
     '"notes": new.notes'),
]
