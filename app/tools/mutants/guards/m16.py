"""Row 16 of MUTANTS_guards.txt: orders_on: view.orders_on reads whether the rule is on, not the `when` latch."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/read/view.py',
     '''orders_on=tuple(when_latch(on) for on in save.latches),''',
     '''orders_on=tuple(rule_on(on) for on in save.latches),'''),
    ('ashfall_app/engine/read/view.py',
     '''from ..orders.orders import AfterTime, Condition, StoreValue, guard_latches, when_latch
''',
     '''from ..orders.orders import AfterTime, Condition, StoreValue, guard_latches, rule_on, when_latch
'''),
]
