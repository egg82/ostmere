"""Row 04 of tests/writer/MUTANTS_queue.txt: the weight has no cap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/budget.py',
     '    return min(budget.weight_cap, 1 + max(0, returning_days))\n',
     '    return 1 + max(0, returning_days)\n'),
]
