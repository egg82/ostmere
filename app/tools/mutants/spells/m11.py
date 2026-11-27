"""Row 11 of MUTANTS.txt: no firing room."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     'max(0, room))\n    if k == 0',
     '10**9)\n    if k == 0'),
]
