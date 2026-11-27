"""Row 01 of MUTANTS_groups.txt: a pooled lane may be declared unruled: its `ruled` is never checked."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/groupchecks.py',
     '        if d.pooled and not d.ruled:\n',
     '        if False:\n'),
]
