"""Row 20 of MUTANTS_guards.txt: codec drops: decode drops an order's `unless`."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/savefile/codec.py',
     '''    return classes[name](**{k: _dec(x, classes) for k, x in v.items() if k != "@"})
''',
     '''    return classes[name](**{k: _dec(x, classes) for k, x in v.items() if k != "@" and not (name == "Order" and k == "unless")})
'''),
]
