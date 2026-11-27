"""Row 24 of MUTANTS_guards.txt: no ready: a guard letting go does not evaluate; its freed lane waits for another event."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '''        return replace(save, latches=save.latches[:i] + (flipped,) + save.latches[i + 1:]), True
''',
     '''        return replace(save, latches=save.latches[:i] + (flipped,) + save.latches[i + 1:]), (
            when_latch(flipped) != when_latch(save.latches[i]) or any(n and not w for n, w in zip(guard_latches(flipped), guard_latches(save.latches[i]))))
'''),
    ('ashfall_app/engine/handlers.py',
     '''from .latches import flipped_now
''',
     '''from .latches import flipped_now
from .orders import guard_latches, when_latch
'''),
]
