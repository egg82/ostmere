"""Row 03 of MUTANTS_or_else.txt: once a fallback tap is chosen the rule keeps it while it can act, though an earlier action can act again (the last choice is remembered, reset when time runs back; loop bound lowered)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/decisions.py',
     '    for _, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            return verb\n    return None\n',
     "    if save.time < _KEPT['t']:\n        _KEPT.clear()\n    _KEPT['t'] = save.time\n    for i, verb, latch in listed(save.orders, save.latches):\n        if (i, verb) == _KEPT.get('v') and rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            return verb\n    for i, verb, latch in listed(save.orders, save.latches):\n        if rule_on(latch) and isinstance(verb, TapCard) and _can_act(save, rules, verb):\n            _KEPT['v'] = (i, verb)\n            return verb\n    return None\n"),
    ('ashfall_app/engine/decisions.py',
     'def _tap_order_verb(save: Save, rules: Rules) -> TapCard | None:\n',
     "_KEPT: dict[str, object] = {'t': -1}\n\n\ndef _tap_order_verb(save: Save, rules: Rules) -> TapCard | None:\n"),
    ('ashfall_app/engine/instant.py',
     '_SETTLE_GUARD = 1_000_000\n',
     '_SETTLE_GUARD = 3_000\n'),
]
