"""Row 20 of MUTANTS_held.txt: the rules encoding writes `while_running: []` for every card."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '            if runner.get("while_running") == []:',
     '            if False:'),
]
RELOCK = True
