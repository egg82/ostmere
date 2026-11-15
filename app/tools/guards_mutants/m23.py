"""Row 23 of MUTANTS_guards.txt: tap source: the tap source reads the `when` latch alone; only the running mix reads guards."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/decisions.py',
     '''        if rule_on(latch) and isinstance(order.then, TapCard) and _can_act(save, rules, order.then):
''',
     '''        if when_latch(latch) and isinstance(order.then, TapCard) and _can_act(save, rules, order.then):
'''),
    ('ashfall_app/engine/decisions.py',
     '''initial_latch, latch_of, rule_on
''',
     '''initial_latch, latch_of, rule_on, when_latch
'''),
]
