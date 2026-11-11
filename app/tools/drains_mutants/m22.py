"""Row 22 of MUTANTS_drains.txt: every_hours ignored."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/convert.py',
     '    return Flow(StoreId(f.store), per_hour(f.items_per_hour) // f.every_hours)\n',
     '    return Flow(StoreId(f.store), per_hour(f.items_per_hour))\n'),
]
