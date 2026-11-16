"""Row 06 of MUTANTS_drains.txt: a drain refuses a tap's start while its store is at 0 (the blocker is back)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '                              for store, q in input_rest(save, rules, c) if store_value(save, store) < q]\n',
     '                              for store, q in input_rest(save, rules, c) if store_value(save, store) < q]\n'
     '    found += [AtLeast(StoreValue(a.store), 1, 1) for a in c.drains if store_value(save, a.store) < 1]\n'),
]
