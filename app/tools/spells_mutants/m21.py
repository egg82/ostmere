"""Row 21 of MUTANTS.txt: link card is none."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '    for key in links:\n        emit(save.time, key, card)\n',
     '    for key in links:\n        emit(save.time, key, None)\n'),
]
