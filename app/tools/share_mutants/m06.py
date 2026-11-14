"""Row 06 of MUTANTS_share.txt: strict at_most."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/sharelevels.py',
     '    return items * Q - (1 if at_most else 0)\n',
     '    return items * Q - (1 if at_most else 0) - (Q if at_most and floor_side else 0)\n'),
]
