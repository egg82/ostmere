"""Row 02 of MUTANTS_or_else.txt: listed() walks the actions last to first."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/orders.py',
     '        for a in o.actions:\n            yield i, a, latch\n',
     '        for a in reversed(o.actions):\n            yield i, a, latch\n'),
]
