"""Row 07 of MUTANTS_guards.txt: all guards: the rule is paused only while every guard is latched."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/orders.py',
     '''        return latch.when and not any(latch.unless)
''',
     '''        return latch.when and not all(latch.unless)
'''),
]
