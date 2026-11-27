"""Row 09 of MUTANTS_guards.txt: reset kept: an equal guarded order has its latches set afresh."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '''        if old == order:
            return on
''',
     '''        if old == order and not order.unless:
            return on
'''),
]
