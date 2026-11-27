"""Row 02 of MUTANTS_groups.txt: a group may name any lane, not only a pooled one."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/groupchecks.py',
     '        if d.group not in pooled:\n',
     '        if False:\n'),
]
