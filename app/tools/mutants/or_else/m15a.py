"""Row 15 of MUTANTS_or_else.txt: retiring reads only `then`: a named fallback stays listed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/orders.py',
     '    actions = tuple(a for a in order.actions if not drop(a))\n',
     '    actions = tuple(a for a in order.actions if not drop(a) or a is not order.then)\n'),
]
