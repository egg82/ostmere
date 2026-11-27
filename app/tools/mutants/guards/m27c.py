"""Row 27 of MUTANTS_guards.txt: or-else limits: a tap and a mix in one rule are accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    require(all(type(a) is kind for a in actions),''',
     '''    require(True or all(type(a) is kind for a in actions),'''),
]
