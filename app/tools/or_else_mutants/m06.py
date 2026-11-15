"""Row 06 of MUTANTS_or_else.txt: no READY event for a listed tap whose lane is free: it starts at the next other event."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/schedule.py',
     '        b = blocker(save, rules, card)\n        if b is None and cascaded:\n',
     '        if next(ls.card for ls in save.lanes if ls.lane == index(rules).cards[card].lane) is None:\n            continue\n        b = blocker(save, rules, card)\n        if b is None and cascaded:\n'),
]
