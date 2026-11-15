"""Row 04 of MUTANTS_guards.txt: when frozen: the `when` latch does not move while a guard holds."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/latches.py',
     '''    t = change_time(save, rules, order.when, when_latch(latch))
''',
     '''    t = None if any(guard_latches(latch)) else change_time(save, rules, order.when, when_latch(latch))
'''),
    ('ashfall_app/engine/latches.py',
     '''    if change_time(save, rules, order.when, when) == save.time:
''',
     '''    if not any(guards) and change_time(save, rules, order.when, when) == save.time:
'''),
]
