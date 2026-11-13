"""Row 03 of tests/db/MUTANTS_clocks.txt: CONNECT_TIMEOUT_S is 30, not 3."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/engine.py',
     'CONNECT_TIMEOUT_S = 3\n',
     'CONNECT_TIMEOUT_S = 30\n'),
]
