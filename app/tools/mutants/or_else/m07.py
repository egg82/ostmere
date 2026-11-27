"""Row 07 of MUTANTS_or_else.txt: a true rule listing a live tap, with none of its taps able to act, ends the search: later rules get no lane (loop bound lowered)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '    for _, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            return verb\n    return None\n',
     '    for i, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard):\n            if _can_act(save, rules, verb):\n                return verb\n            if not any(isinstance(a, TapCard) and _can_act(save, rules, a) for a in save.orders[i].actions) and not plan.is_dead(save, rules, verb):\n                return None\n    return None\n'),
    ('ashfall_app/engine/loop/instant.py',
     '_SETTLE_GUARD = 1_000_000\n',
     '_SETTLE_GUARD = 3_000\n'),
]
