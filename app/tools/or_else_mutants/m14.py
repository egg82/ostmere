"""Row 14 of MUTANTS_or_else.txt: naming one action of a rule retires the whole rule."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders.py',
     '    if not actions:\n        return None\n',
     '    if not actions or len(actions) != len(order.actions):\n        return None\n'),
]
