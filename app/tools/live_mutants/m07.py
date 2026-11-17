"""Row 07 of tests/writer/MUTANTS_live.txt: a max_tokens stop is returned as the line."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '{"refusal": "refused", "max_tokens": "truncated"}',
     '{"refusal": "refused"}'),
]
