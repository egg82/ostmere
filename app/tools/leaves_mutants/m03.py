"""Row 03 of MUTANTS_leaves.txt, m03: pays the task: the tap under way at the leave is not ended."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '        if ls.card is not None and counts.is_retired(save, rules, ls.card):\n',
     '        if ls.card is not None and counts.is_retired(save, rules, ls.card) and not any(\n                u.kind.value == "left" and u.id == ls.lane for u in save.unlocked):\n'),
]
