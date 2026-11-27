"""Row 24 of MUTANTS.txt: uncapped no chain."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/loop/handlers.py',
     '    if (c.cap is None and c.chain is None) or work_value',
     '    if c.cap is None or work_value'),
]
