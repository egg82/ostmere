"""Row 15 of MUTANTS_or_else.txt: retiring reads only the fallbacks: a named first action stays at the head."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders.py',
     '    actions = tuple(a for a in order.actions if not drop(a))\n',
     '    actions = tuple(a for a in order.actions if not drop(a) or a is order.then)\n'),
]
