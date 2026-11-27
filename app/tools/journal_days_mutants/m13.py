"""Row 13 of tests/saves/journal/MUTANTS_journal_days.txt: every note is served in ink, whatever its slot names."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/service.py',
     'hand=jm.Hand(look.hand)',
     'hand=jm.Hand.INK'),
]
