"""Row 20 of MUTANTS_guards.txt: codec drops: decode drops a GuardedLatch's guard bools."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/savefile/codec.py',
     '''    return classes[name](**{k: _dec(x, classes) for k, x in v.items() if k != "@"})
''',
     '''    return classes[name](**{k: (() if (name == "GuardedLatch" and k == "unless") else _dec(x, classes)) for k, x in v.items() if k != "@"})
'''),
]
