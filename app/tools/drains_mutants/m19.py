"""Row 19 of MUTANTS_drains.txt: an inexact every_hours is rounded down, not refused."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/refs.py',
     '        if per_hour(f.items_per_hour) % f.every_hours != 0:\n',
     '        if False:\n'),
]
