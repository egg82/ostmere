"""Row 19 of MUTANTS_guards.txt: latch form: a rule with no guard has a GuardedLatch, not a bool."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders.py',
     '''    return GuardedLatch(when, guards) if guards else when
''',
     '''    return GuardedLatch(when, guards)
'''),
]
