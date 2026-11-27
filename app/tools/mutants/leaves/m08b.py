"""Row 08 of MUTANTS_leaves.txt, m08b: too many orders: lb's orders go with la's (the orders of every ruled lane)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/leaves.py',
     'from ..core.ids import CardId\n',
     'from ..core.ids import HANDS, CardId\n'),
    ('ashfall_app/engine/people/leaves.py',
     '    save = without_taps(replace(save, unlocked=unlocked), cards)\n',
     '    save = without_taps(replace(save, unlocked=unlocked), frozenset(c.id for c in rules.cards if c.lane != HANDS))\n'),
]
