"""Row 03 of tests/writer/MUTANTS_queue.txt: every world weighs 1."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/budget.py',
     '    return min(budget.weight_cap, 1 + max(0, returning_days))\n',
     '    return 1\n'),
]
