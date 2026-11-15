"""Row 05 of MUTANTS_guards.txt: polled: a guard's letting go is not solved as an event."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/latches.py',
     '''        g = change_time(save, rules, cond, on)
''',
     '''        g = None if on else change_time(save, rules, cond, on)
'''),
]
