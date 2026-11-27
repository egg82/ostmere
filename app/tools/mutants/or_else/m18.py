"""Row 18 of MUTANTS_or_else.txt: a dead tap is chosen as able to act, and nothing starts (loop bound lowered)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/decisions.py',
     '    for _, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            return verb\n    return None\n',
     '    for _, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard) and (_can_act(save, rules, verb) or plan.is_dead(save, rules, verb)):\n            return verb\n    return None\n'),
    ('ashfall_app/engine/instant.py',
     '_SETTLE_GUARD = 1_000_000\n',
     '_SETTLE_GUARD = 3_000\n'),
]
