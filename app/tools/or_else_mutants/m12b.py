"""Row 12 of MUTANTS_or_else.txt: a rule paused by a guard runs its fallback mix while its first mix is greyed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/plan.py',
     '        if rule_on(latch) and isinstance(a, SwitchMix) and a.mix in saved and not greyed(save, rules, a.mix) \\\n                and mix_layer(rules, save.mixes, a.mix) is layer:\n            return i, a.mix\n    return None\n',
     "        first = save.orders[i].then\n        if not rule_on(latch) and getattr(latch, 'when', latch) and isinstance(a, SwitchMix) and a != first and isinstance(first, SwitchMix) \\\n                and first.mix in saved and greyed(save, rules, first.mix) and a.mix in saved and not greyed(save, rules, a.mix) \\\n                and mix_layer(rules, save.mixes, a.mix) is layer:\n            return i, a.mix\n        if rule_on(latch) and isinstance(a, SwitchMix) and a.mix in saved and not greyed(save, rules, a.mix) \\\n                and mix_layer(rules, save.mixes, a.mix) is layer:\n            return i, a.mix\n    return None\n"),
]
