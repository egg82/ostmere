"""Row 30 of MUTANTS.txt: chain with no tally."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chaincheck.py',
     '    _require(f.fought is not None and f.chained is not None,',
     '    _require(True,'),
]
