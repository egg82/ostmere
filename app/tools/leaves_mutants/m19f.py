"""Row 19 of MUTANTS_leaves.txt, m19f: validation: LEFT in Rules.opening is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rules_check.py',
     '        _require(u.kind not in PRESENT_ONLY, f"opening:',
     '        _require(u.kind not in PRESENT_ONLY or u.kind.value == "left", f"opening:'),
]
