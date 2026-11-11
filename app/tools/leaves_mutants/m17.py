"""Row 17 of MUTANTS_leaves.txt, m17: empty mix goes: a mix left with no component is deleted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    return replace(save, mixes=tuple(_without(m, cards) for m in save.mixes),\n',
     '    return replace(save, mixes=tuple(m for m in (_without(m, cards) for m in save.mixes) if m.components),\n'),
]
