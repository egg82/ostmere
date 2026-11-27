"""Row 07 of MUTANTS.txt: run reach is base."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     '    k = min(due(save, rules, chain.runner), reach(save, rules, card).value, max(0, room))\n',
     '    k = min(due(save, rules, chain.runner), chain.reach, max(0, room))\n'),
]
