"""Row 12 of tests/db/MUTANTS_clocks.txt: a hands-free claim ignores an earlier send, so two jobs both win."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/handsfree.py',
     '        s.hands_free_sent.is_distinct_from(s.hands_free_at),\n',
     ''),
]
