"""Row 35 of MUTANTS.txt: fight view chained."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/read/fightview.py',
     '0 if f.chained is None else _count(save, rules, f.chained))',
     '0)'),
]
