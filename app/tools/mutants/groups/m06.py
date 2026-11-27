"""Row 06 of MUTANTS_groups.txt: a mark may clear the mark of a lane with no group."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/groupchecks.py',
     '    if not m.own_split and _group_of(rules, m.lane) is None:\n',
     '    if False:\n'),
]
