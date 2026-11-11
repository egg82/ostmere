"""Row 19 of MUTANTS_leaves.txt, m19l: loader: joined or left in an outcome's unlocks is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/checks.py',
     '        if u.unlock_kind in ("joined", "left"):\n',
     '        if False:\n'),
]
