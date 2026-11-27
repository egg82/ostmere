"""Row 05 of MUTANTS_drains.txt: a completion takes one unit more than A' (rounded up twice)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/lumps.py',
     '    return card.inputs + card.drains + (',
     '    return card.inputs + tuple(Amount(a.store, a.quantity + 1) for a in card.drains) + ('),
]
