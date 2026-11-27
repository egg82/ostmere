"""Row 27 of MUTANTS_guards.txt: or-else limits: mixes of two layers are accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    require(len(layers) <= 1,''',
     '''    require(len(layers) <= 2,'''),
]
