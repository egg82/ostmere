"""Row 02 of MUTANTS.txt: latest."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/casts.py',
     '    return running[0] if running else None\n',
     '    return running[-1] if running else None\n'),
]
