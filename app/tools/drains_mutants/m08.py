"""Row 08 of MUTANTS_drains.txt: forgiveness reaches inputs: a card's input stores are read as drained."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/lumps.py',
     '        for a in c.drains:\n',
     '        for a in (*c.drains, *c.inputs):\n'),
]
