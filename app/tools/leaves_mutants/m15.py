"""Row 15 of MUTANTS_leaves.txt, m15: lands on the gone: a join of a left lane is applied."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/joins.py',
     '        if not is_joined(save, rules, j.lane) and not is_left(save, j.lane):\n',
     '        if not is_joined(save, rules, j.lane):\n'),
]
