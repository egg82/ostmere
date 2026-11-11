"""Row 01 of MUTANTS_leaves.txt, m01: greys the mix: a leave takes no share out of a saved mix, so the mixes holding la's cards grey."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    return replace(save, mixes=tuple(_without(m, cards) for m in save.mixes),\n',
     '    return replace(save, mixes=save.mixes,\n'),
]
