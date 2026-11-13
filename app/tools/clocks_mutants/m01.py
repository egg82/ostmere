"""Row 01 of tests/db/MUTANTS_clocks.txt: no connect_timeout is added."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/engine.py',
     '{"connect_timeout": CONNECT_TIMEOUT_S, **TCP_SETTINGS}.items()',
     '{**TCP_SETTINGS}.items()'),
]
