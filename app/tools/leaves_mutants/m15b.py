"""Row 15 of MUTANTS_leaves.txt, m15b: lands on the gone: an install on a left lane is applied."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    return tuple(i for i in installs if not is_left(save, cards[i.card].lane))\n',
     '    return installs\n'),
]
