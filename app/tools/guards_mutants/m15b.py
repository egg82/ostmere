"""Row 15 of MUTANTS_guards.txt: paused named: a paused rule is shown as waiting."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/plan.py',
     '''        if not rule_on(latch):
            return OrderState.PAUSED
''',
     '''        if not rule_on(latch):
            return OrderState.WAITING
'''),
]
