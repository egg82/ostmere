"""Row 01 of MUTANTS_or_else.txt: only `then` is listed: listed() yields no fallback."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders.py',
     '        for a in o.actions:\n            yield i, a, latch\n',
     '        for a in (o.then,):\n            yield i, a, latch\n'),
]
