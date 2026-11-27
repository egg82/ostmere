"""Row 03 of tests/writer/MUTANTS_live.txt: an empty reply is returned as the line."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '("" if text else "empty")',
     '""'),
]
