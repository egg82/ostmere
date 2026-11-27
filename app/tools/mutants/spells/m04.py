"""Row 04 of MUTANTS.txt: due leaves one out."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     '    return members - done % members\n',
     '    return max(0, members - 1 - done % members)\n'),
]
