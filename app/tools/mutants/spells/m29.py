"""Row 29 of MUTANTS.txt: empty chain."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chaincheck.py',
     '    _require(chain.reach >= 1,',
     '    _require(True,'),
    ('ashfall_app/engine/chaincheck.py',
     '    _require(len(chain.lines) >= 1,',
     '    _require(True,'),
]
