"""Row 25 of MUTANTS_leaves.txt, m25: lands again: every evaluation removes the orders tapping the cards a fired trigger retires."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/instant.py',
     '    verb = controlling_verb(save, rules)\n    if verb is None:\n        return save, 0, False\n',
     '    from .installs import without_taps\n    save = without_taps(save, frozenset(c for t, f in zip(rules.triggers, save.fired) if f for c in t.outcome.retire_orders))\n    verb = controlling_verb(save, rules)\n    if verb is None:\n        return save, 0, False\n'),
]
