"""Row 19 of MUTANTS_leaves.txt, m19e: validation: LEFT in Outcome.unlocks is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rules_check.py',
     '    _require(not any(u.kind in PRESENT_ONLY for u in o.unlocks),',
     '    _require(not any(u.kind in PRESENT_ONLY and u.kind.value != "left" for u in o.unlocks),'),
]
