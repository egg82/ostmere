"""Row 08 of MUTANTS_leaves.txt, m08b: too many orders: lb's orders go with la's (the orders of every ruled lane)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     'from .ids import CardId\n',
     'from .ids import HANDS, CardId\n'),
    ('ashfall_app/engine/leaves.py',
     '    save = without_taps(replace(save, unlocked=unlocked), cards)\n',
     '    save = without_taps(replace(save, unlocked=unlocked), frozenset(c.id for c in rules.cards if c.lane != HANDS))\n'),
]
