"""Row 25 of MUTANTS_guards.txt: memoryless: each advance sets every guard latch afresh from its threshold."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/core/api.py',
     '''    stopping = False
    while True:
        upcoming = [e for e in events(save, rules) if e.time > save.time]
''',
     '''    from dataclasses import replace as _replace
    from ..orders.decisions import latch_now
    from ..orders.orders import latch_of, when_latch
    save = _replace(save, latches=tuple(latch_of(when_latch(on), tuple(latch_now(save, rules, g) for g in o.unless))
                                        for o, on in zip(save.orders, save.latches)))
    stopping = False
    while True:
        upcoming = [e for e in events(save, rules) if e.time > save.time]
'''),
]
