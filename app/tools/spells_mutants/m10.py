"""Row 10 of MUTANTS.txt: link key off index."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     'chain.lines[min(i, len(chain.lines)) - 1]',
     'chain.lines[0]'),
]
