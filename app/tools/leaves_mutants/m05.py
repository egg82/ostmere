"""Row 05 of MUTANTS_leaves.txt, m05: stops still run: no standing action is ever stopped."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/gone.py',
     '    return frozenset(a for lane in gone for a in stops.get(LaneId(lane), ()))\n',
     '    return frozenset()\n'),
]
