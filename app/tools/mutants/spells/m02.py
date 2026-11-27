"""Row 02 of MUTANTS.txt: longer than due."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     '    k = min(due(save, rules, chain.runner), reach(save, rules, card).value, max(0, room))\n',
     '    k = min(reach(save, rules, card).value, max(0, room))\n'),
]
