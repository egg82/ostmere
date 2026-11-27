"""Row 07 of tests/saves/journal/MUTANTS_journal_days.txt: a line of two causes feeds only the first's subject."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'for source in j.sources.get(key, ())), key=lambda ln: ln.at)',
     'for source in j.sources.get(key, ())[:1]), key=lambda ln: ln.at)'),
]
