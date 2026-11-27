"""Row 03 of MUTANTS_guards.txt: lets go: a guard coming on sets the `when` latch false."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/latches.py',
     '''            return latch_of(when, guards[:j] + (not on,) + guards[j + 1:])
''',
     '''            return latch_of(when and on, guards[:j] + (not on,) + guards[j + 1:])
'''),
]
