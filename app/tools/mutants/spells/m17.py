"""Row 17 of MUTANTS.txt: mixed no chain."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/loop/handlers.py',
     '    if c.chain is None:\n        return save, True, 0\n',
     '    if c.chain is None or not any(ls.card == card for ls in save.lanes):\n        return save, True, 0\n'),
]
