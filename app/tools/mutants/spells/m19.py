"""Row 19 of MUTANTS.txt: capped no chain."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/loop/handlers.py',
     '    if c.chain is None:\n        return save, True, 0\n',
     '    if c.chain is None or c.cap is not None:\n        return save, True, 0\n'),
]
