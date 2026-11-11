"""Row 20 of MUTANTS_spent.txt: a lane whose rest has share 0 divides by zero instead of moving nothing."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     '        if total == 0:\n            continue\n',
     '        if total == 0 and not given:\n            continue\n'),
]
