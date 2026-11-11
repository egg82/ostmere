"""Row 11 of MUTANTS_drains.txt: at 0 with n > d the store stays at 0."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/lumps.py',
     '    return others >= 0 > others + drained\n',
     '    return others >= 0\n'),
]
