"""Row 04 of tests/db/MUTANTS_clocks.txt: a checkout waits 3 s whatever timeout_s the caller gave."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/engine.py',
     'max_size=max_size, timeout=timeout_s,',
     'max_size=max_size, timeout=3,'),
]
