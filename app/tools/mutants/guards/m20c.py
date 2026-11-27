"""Row 20 of MUTANTS_guards.txt: codec drops: encode drops an order's `unless`."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '''    return (key not in _OMITTED_WHEN_EMPTY or bool(value)) and value != _OMITTED_AT_DEFAULT.get(key, object())
''',
     '''    return key != ("Order", "unless") and (key not in _OMITTED_WHEN_EMPTY or bool(value)) and value != _OMITTED_AT_DEFAULT.get(key, object())
'''),
]
