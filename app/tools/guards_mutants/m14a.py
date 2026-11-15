"""Row 14 of MUTANTS_guards.txt: state order: paused is judged before waiting."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/plan.py',
     '''        if all(is_dead(save, rules, a) for a in o.actions):
            return OrderState.PASSED_OVER
        if not when_latch(latch):
            return OrderState.WAITING
        if not rule_on(latch):
            return OrderState.PAUSED
''',
     '''        if all(is_dead(save, rules, a) for a in o.actions):
            return OrderState.PASSED_OVER
        if not isinstance(latch, bool) and any(latch.unless):
            return OrderState.PAUSED
        if not when_latch(latch):
            return OrderState.WAITING
'''),
]
