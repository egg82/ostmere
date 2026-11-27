"""Row 08 of MUTANTS.txt: random length."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     'from dataclasses import dataclass\n',
     'import random\nfrom dataclasses import dataclass\n'),
    ('ashfall_app/engine/combat/chains.py',
     '    k = min(due(save, rules, chain.runner), reach(save, rules, card).value, max(0, room))\n',
     '    k = random.randint(0, min(due(save, rules, chain.runner), reach(save, rules, card).value, max(0, room)))\n'),
]
