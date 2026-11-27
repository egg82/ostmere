"""Row 09 of MUTANTS.txt: lines folded."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     '    links = tuple(chain.lines[min(i, len(chain.lines)) - 1] for i in range(1, k + 1))\n',
     '    links = (chain.lines[0],)\n'),
]
