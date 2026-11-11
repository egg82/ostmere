"""Row 27 of MUTANTS_leaves.txt, m27: restarts it: a retired card is tapped again ahead of the orders whenever it can start."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/instant.py',
     '    verb = controlling_verb(save, rules)\n    if verb is None:\n        return save, 0, False\n',
     '    from .lanes import TapCard\n    from .work import tap\n    again = save\n    for t, f in zip(rules.triggers, save.fired):\n        for c in (t.outcome.retire_orders if f else ()):\n            again = tap(again, rules, TapCard(c), False)\n    if again is not save:\n        return again, 1, True\n    verb = controlling_verb(save, rules)\n    if verb is None:\n        return save, 0, False\n'),
]
