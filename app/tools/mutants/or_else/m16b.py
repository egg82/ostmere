"""Row 16 of MUTANTS_or_else.txt: a rule that keeps an action has its latches set true (its guards false)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/installs.py',
     'initial_latch, pruned, rule_on\n',
     'initial_latch, latch_of, pruned, rule_on\n'),
    ('ashfall_app/engine/orders/installs.py',
     '            kept.append((p, on))\n',
     '            kept.append((p, on if p == o else latch_of(True, (False,) * len(o.unless))))\n'),
]
