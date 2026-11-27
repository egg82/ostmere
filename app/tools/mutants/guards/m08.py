"""Row 08 of MUTANTS_guards.txt: fresh off: SetOrders sets each guard latch false instead of reading its threshold."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '''    return latch_of(latch_now(save, rules, order.when), tuple(latch_now(save, rules, g) for g in order.unless))
''',
     '''    return latch_of(latch_now(save, rules, order.when), tuple(False for g in order.unless))
'''),
]
