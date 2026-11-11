"""Row 17 of MUTANTS_drains.txt: the drains' blocker is read before the inputs'."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    found: list[Condition] = [AtLeast(StoreValue(store), q, q)\n                              for store, q in input_rest(save, rules, c) if store_value(save, store) < q]\n    found += [AtLeast(StoreValue(a.store), 1, 1) for a in c.drains if store_value(save, a.store) < 1]\n',
     '    found: list[Condition] = [AtLeast(StoreValue(a.store), 1, 1) for a in c.drains if store_value(save, a.store) < 1]\n    found += [AtLeast(StoreValue(store), q, q)\n                              for store, q in input_rest(save, rules, c) if store_value(save, store) < q]\n'),
]
