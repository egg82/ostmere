"""Row 26 of MUTANTS_guards.txt: forecast: the forecast plays the rules as if they held no guard."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/forecast.py',
     '''    s, n = save, 0
''',
     '''    from dataclasses import replace
    from .orders import when_latch
    s, n = replace(save, orders=tuple(replace(o, unless=()) for o in save.orders),
                   latches=tuple(when_latch(on) for on in save.latches)), 0
'''),
]
