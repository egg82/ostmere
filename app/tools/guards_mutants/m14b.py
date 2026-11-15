"""Row 14 of MUTANTS_guards.txt: state order: paused is judged before passed over."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/plan.py',
     '''        if is_dead(save, rules, verb):
            return OrderState.PASSED_OVER
        if not when_latch(latch):
            return OrderState.WAITING
        if not rule_on(latch):
            return OrderState.PAUSED
''',
     '''        if not isinstance(latch, bool) and any(latch.unless):
            return OrderState.PAUSED
        if is_dead(save, rules, verb):
            return OrderState.PASSED_OVER
        if not when_latch(latch):
            return OrderState.WAITING
'''),
]
