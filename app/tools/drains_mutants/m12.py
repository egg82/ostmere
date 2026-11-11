"""Row 12 of MUTANTS_drains.txt: drains left out of the rules encoding even when non-empty."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/codec.py',
     '            if runner.get("drains") == []:\n',
     '            if "drains" in runner:\n'),
]
