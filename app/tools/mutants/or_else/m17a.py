"""Row 17 of MUTANTS_or_else.txt: a rule whose every action is named stays with its last action."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/orders.py',
     '    if not actions:\n        return None\n',
     '    if not actions:\n        return replace(order, then=order.actions[-1], or_else=())\n'),
]
