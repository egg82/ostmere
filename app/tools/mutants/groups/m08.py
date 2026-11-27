"""Row 08 of MUTANTS_groups.txt: a join of a pooled lane is valid."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/groupchecks.py',
     '    if j.lane not in lanes or not lanes[j.lane].ruled or lanes[j.lane].pooled:\n',
     '    if j.lane not in lanes or not lanes[j.lane].ruled:\n'),
]
