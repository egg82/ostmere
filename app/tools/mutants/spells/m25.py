"""Row 25 of MUTANTS.txt: chain at the wrong instant."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/loop/handlers.py',
     '    for key in links:\n        emit(save.time, key, card)\n',
     '    for key in links:\n        emit(save.time + 1, key, card)\n'),
]
