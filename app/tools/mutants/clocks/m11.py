"""Row 11 of tests/db/MUTANTS_clocks.txt: MAX_INSTANTS is 4."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/forecast.py',
     'MAX_INSTANTS = 400\n',
     'MAX_INSTANTS = 4\n'),
]
