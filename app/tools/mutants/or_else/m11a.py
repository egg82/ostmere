"""Row 11 of MUTANTS_or_else.txt: a guard stops only a rule's first action: fallbacks are read with the `when` latch alone."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/orders.py',
     '        for a in o.actions:\n            yield i, a, latch\n',
     '        for k, a in enumerate(o.actions):\n            yield i, a, (latch if k == 0 else when_latch(latch))\n'),
]
