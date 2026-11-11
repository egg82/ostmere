"""Row 12 of MUTANTS_leaves.txt, m12: still tappable: a left lane's cards are not retired, so a tap, a SaveMix and an order's tap act on them."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/counts.py',
     '    return named | left_cards(save, rules)\n',
     '    return named\n'),
]
