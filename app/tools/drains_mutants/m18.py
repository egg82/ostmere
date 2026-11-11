"""Row 18 of MUTANTS_drains.txt: validation accepts a drained store that is also on another of the card's lines."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/drains.py',
     '        if a.store in listed or a.store in fought:\n',
     '        if False:\n'),
]
