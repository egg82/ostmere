"""Row 12 of MUTANTS_or_else.txt: a rule paused by a guard runs its fallback tap while its first tap cannot act."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/decisions.py',
     '    for _, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            return verb\n    return None\n',
     "    for i, verb, latch in listed(save.orders, save.latches):\n        if isinstance(verb, TapCard) and getattr(latch, 'when', latch) and not rule_on(latch) and verb != save.orders[i].then \\\n                and isinstance(save.orders[i].then, TapCard) and not _can_act(save, rules, save.orders[i].then) and _can_act(save, rules, verb):\n            return verb\n        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            return verb\n    return None\n"),
]
