"""Row 05 of tests/writer/MUTANTS_live.txt: the live client is built without a key."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '    if not key:\n',
     '    if False:\n'),
]
