"""Row 04 of MUTANTS_leaves.txt, m04: keeps the orders: the orders tapping la's cards stay in save.orders."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    save = without_taps(replace(save, unlocked=unlocked), cards)\n',
     '    save = replace(save, unlocked=unlocked)\n'),
]
