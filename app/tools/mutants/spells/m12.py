"""Row 12 of MUTANTS.txt: room off by one."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/instant.py',
     '            room = rules.max_firings_per_instant - firings - 1\n',
     '            room = rules.max_firings_per_instant - firings\n'),
]
