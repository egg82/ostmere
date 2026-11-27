"""Row 02 of tests/db/MUTANTS_clocks.txt: connect_timeout is set even when the URL sets its own."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/engine.py',
     'if k not in set_by_url})',
     'if k not in set_by_url or k == "connect_timeout"})'),
]
