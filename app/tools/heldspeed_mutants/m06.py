"""Row 06 of MUTANTS_heldspeed.txt: validation accepts HANDS."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/fightcheck.py',
     '        _require(ln in {d.id for d in rules.lanes}, ',
     '        _require(ln in {d.id for d in rules.lanes} or ln == "hands", '),
]
