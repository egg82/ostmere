"""Row 06 of MUTANTS_drains.txt: a tap with x = 0 is ready: the drain's blocker never fires."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    found += [AtLeast(StoreValue(a.store), 1, 1) for a in c.drains if store_value(save, a.store) < 1]\n',
     '    found += [AtLeast(StoreValue(a.store), 1, 1) for a in c.drains if store_value(save, a.store) < 0]\n'),
]
