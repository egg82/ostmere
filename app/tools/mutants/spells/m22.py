"""Row 22 of MUTANTS.txt: reach rounds up."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/strengthmath.py',
     '    value = base * add_factor * prod(m.amount_bp for m in muls) // BP ** (1 + len(muls))\n',
     '    value = -(-(base * add_factor * prod(m.amount_bp for m in muls)) // BP ** (1 + len(muls)))\n'),
]
