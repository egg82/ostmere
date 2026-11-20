"""Row 03 of MUTANTS_groups.txt: a card on a pooled lane may carry a cap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/groupchecks.py',
     '        if c.lane in pooled and c.cap is not None:\n',
     '        if False:\n'),
]
