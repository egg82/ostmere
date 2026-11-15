"""Row 27 of MUTANTS_guards.txt: or-else limits: a fourth action is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/checks.py',
     '''    require(len(actions) <= MAX_ACTIONS,''',
     '''    require(len(actions) <= MAX_ACTIONS + 1,'''),
]
