"""Row 10 of MUTANTS_or_else.txt: a true rule whose listed mix of the layer is greyed gives the layer to the player's own mix, not its next mix."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/plan.py',
     '        if rule_on(latch) and isinstance(a, SwitchMix) and a.mix in saved and not greyed(save, rules, a.mix) \\\n                and mix_layer(rules, save.mixes, a.mix) is layer:\n            return i, a.mix\n    return None\n',
     '        if rule_on(latch) and isinstance(a, SwitchMix) and a.mix in saved and greyed(save, rules, a.mix) \\\n                and mix_layer(rules, save.mixes, a.mix) is layer:\n            return None\n        if rule_on(latch) and isinstance(a, SwitchMix) and a.mix in saved and not greyed(save, rules, a.mix) \\\n                and mix_layer(rules, save.mixes, a.mix) is layer:\n            return i, a.mix\n    return None\n'),
]
