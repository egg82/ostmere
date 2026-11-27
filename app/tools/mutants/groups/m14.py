"""Row 14 of MUTANTS_groups.txt: a group card runs at its members' lane speed as well as the group's."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rates.py',
     '        speed.append(LaneSpeed(lane))\n',
     '        speed.append(LaneSpeed(lane))\n        speed += [LaneSpeed(d.id) for d in rules.lanes if d.group == lane]\n'),
]
