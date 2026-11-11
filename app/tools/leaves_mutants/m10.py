"""Row 10 of MUTANTS_leaves.txt, m10: lane held: the lane of a retired card is not freed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     'counts.is_retired(save, rules, ls.card):\n            save = _free(save, ls.lane)\n',
     'counts.is_retired(save, rules, ls.card):\n            save = save\n'),
]
