"""Row 21 of MUTANTS_guards.txt: limits: a fourth guard is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    require(len(guards) <= MAX_GUARDS,''',
     '''    require(len(guards) <= MAX_GUARDS + 1,'''),
]
