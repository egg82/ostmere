"""Row 01 of MUTANTS_guards.txt: one bit: every guard's latch moves as any one guard's does."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/latches.py',
     '''            return latch_of(when, guards[:j] + (not on,) + guards[j + 1:])
''',
     '''            return latch_of(when, (not on,) * len(guards))
'''),
    ('ashfall_app/engine/instant.py',
     '''_SETTLE_GUARD = 1_000_000
''',
     '''_SETTLE_GUARD = 3_000
'''),
]
