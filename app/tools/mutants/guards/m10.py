"""Row 10 of MUTANTS_guards.txt: equal sans: orders matched ignoring `unless`."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '''        if old == order:
            return on
''',
     '''        if replace(old, unless=()) == replace(order, unless=()):
            return on
'''),
]
