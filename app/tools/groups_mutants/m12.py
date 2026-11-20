"""Row 12 of MUTANTS_groups.txt: a tap on a member does not take them out of the crew."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/groups.py',
     'len(m - busy)',
     'len(m)'),
]
