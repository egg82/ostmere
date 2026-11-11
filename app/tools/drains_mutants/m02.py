"""Row 02 of MUTANTS_drains.txt: the drain store at 0 pauses the cure in the mix."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/mixruns.py',
     '        return Run(RunKind.PAUSED, 0, 1, paused_on)\n    unmet = first_unmet(save, rules, index(rules).cards[card])\n',
     '        return Run(RunKind.PAUSED, 0, 1, paused_on)\n    from .rates import store_value\n    dry = [a.store for a in index(rules).cards[card].drains if store_value(save, a.store) == 0]\n    if dry:\n        return Run(RunKind.PAUSED, 0, 1, dry[0])\n    unmet = first_unmet(save, rules, index(rules).cards[card])\n'),
]
