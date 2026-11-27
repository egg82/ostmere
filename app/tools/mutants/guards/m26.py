"""Row 26 of MUTANTS_guards.txt: forecast: the forecast plays the rules as if they held no guard."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/lookahead/forecast.py',
     '''    s, came, own, n, hands = save, tuple[Event, ...](), None, 0, hands_at_start(save, rules)
''',
     '''    from dataclasses import replace
    from ..orders.orders import when_latch
    s, came, own, n, hands = (replace(save, orders=tuple(replace(o, unless=()) for o in save.orders),
                                      latches=tuple(when_latch(on) for on in save.latches)),
                              tuple[Event, ...](), None, 0, hands_at_start(save, rules))
'''),
]
