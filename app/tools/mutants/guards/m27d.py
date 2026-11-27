"""Row 27 of MUTANTS_guards.txt: or-else limits: taps on two lanes are accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/checks.py',
     '''    require(len(lanes) <= 1,''',
     '''    require(len(lanes) <= 2,'''),
]
