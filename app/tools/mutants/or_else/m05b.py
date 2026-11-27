"""Row 05 of MUTANTS_or_else.txt: a rule is passed over when any one action is dead."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/plan.py',
     '        if all(is_dead(save, rules, a) for a in o.actions):\n',
     '        if any(is_dead(save, rules, a) for a in o.actions):\n'),
]
