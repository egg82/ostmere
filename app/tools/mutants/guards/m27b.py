"""Row 27 of MUTANTS_guards.txt: or-else limits: an action listed twice is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    require(len(set(actions)) == len(actions),''',
     '''    require(True or len(set(actions)) == len(actions),'''),
]
