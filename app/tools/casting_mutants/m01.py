"""Row 01 of MUTANTS.txt: counts a group."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/casts.py',
     '        card = pattern.replace(LANE_TOKEN, lane)\n        return card if lane in town.get(pattern, ()) and card in cards else None\n',
     '        g = next((x.group for x in o.lanes if x.id == lane and x.group), lane)\n        card = pattern.replace(LANE_TOKEN, g)\n        return card if g in town.get(pattern, ()) and card in cards else None\n'),
]
