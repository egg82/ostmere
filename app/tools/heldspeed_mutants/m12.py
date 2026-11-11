"""Row 12 of MUTANTS_heldspeed.txt: standing actions keep while_running: [] in the encoding."""
RELOCK = True
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '            if runner.get("while_running") == []:',
     '            if runner.get("while_running") == [] and name == "cards":'),
]
