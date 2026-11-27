"""Row 18 of MUTANTS_guards.txt: empty written: the codec writes `unless` while empty."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/savefile/codec.py',
     '''_OMITTED_WHEN_EMPTY = frozenset({("Order", "unless"), ("Order", "or_else"), ("Outcome", "joins"),''',
     '''_OMITTED_WHEN_EMPTY = frozenset({("Order", "or_else"), ("Outcome", "joins"),'''),
]
