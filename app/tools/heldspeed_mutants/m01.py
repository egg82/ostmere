"""Row 01 of MUTANTS_heldspeed.txt: a standing holder keeps its entries while paused."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    return {a.id: BP if a.id not in paused and a.id not in gone',
     '    return {a.id: BP if a.id not in gone'),
]
