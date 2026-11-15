"""Row 12 of tests/saves/MUTANTS_journal_days.txt: a day not written is served."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/service.py',
     'for n in d.notes for look in (looks.get((n.subject, n.slot), PLAIN),)]) for d in days if d.notes]',
     'for n in d.notes for look in (looks.get((n.subject, n.slot), PLAIN),)]) for d in days]'),
]
