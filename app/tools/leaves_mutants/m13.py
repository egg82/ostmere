"""Row 13 of MUTANTS_leaves.txt, m13: stops them all: every standing action stops."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/gone.py',
     '    return frozenset(a for lane in gone for a in stops.get(LaneId(lane), ()))\n',
     '    return frozenset(a.id for a in rules.standing)\n'),
]
