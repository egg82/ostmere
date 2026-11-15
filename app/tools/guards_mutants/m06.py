"""Row 06 of MUTANTS_guards.txt: cancels tap: a guard coming on mid-tap ends the running tap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '''        return replace(save, latches=save.latches[:i] + (flipped,) + save.latches[i + 1:]), True
''',
     '''        new = replace(save, latches=save.latches[:i] + (flipped,) + save.latches[i + 1:])
        then = save.orders[i].then
        was, now = guard_latches(save.latches[i]), guard_latches(flipped)
        if hasattr(then, "card") and any(n and not w for n, w in zip(now, was)):
            from .index import index
            from .work import interrupt
            new = interrupt(new, rules, index(rules).cards[then.card].lane)
        return new, True
'''),
    ('ashfall_app/engine/handlers.py',
     '''from .latches import flipped_now
''',
     '''from .latches import flipped_now
from .orders import guard_latches
'''),
]
