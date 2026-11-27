"""Row 11 of MUTANTS_heldspeed.txt: validation accepts amount 0 on a HeldSpeed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/fightcheck.py',
     '        _require(w.amount_bp >= 1, ',
     '        _require(w.amount_bp >= 1 or isinstance(w, HeldSpeed), '),
]
