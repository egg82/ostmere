"""Row 23 of MUTANTS_guards.txt: tap source: the tap source reads the `when` latch alone; only the running mix reads guards."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '''        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):
''',
     '''        if when_latch(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):
'''),
    ('ashfall_app/engine/orders/decisions.py',
     '''initial_latch, latch_of, listed, rule_on
''',
     '''initial_latch, latch_of, listed, rule_on, when_latch
'''),
]
