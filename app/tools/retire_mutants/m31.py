"""Row 31 of MUTANTS_leaves.txt, m31: loader lenient: a named card that cures no chip of a season's chores is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/retire_checks.py',
     '            if not any(cures_chip(rules, CardId(card), chip) for chip in chores):\n',
     '            if False:\n'),
]
