"""Row 13 of MUTANTS_drains.txt: the rules encoding writes `drains: []` for every card."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '            if runner.get("drains") == []:\n',
     '            if False:\n'),
]
RELOCK = True
