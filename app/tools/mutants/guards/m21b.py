"""Row 21 of MUTANTS_guards.txt: limits: a guard listed twice is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    require(len(set(guards)) == len(guards), "a rule holds no guard twice")
''',
     ''''''),
]
