"""Row 16 of MUTANTS_or_else.txt: a rule that keeps an action has its latches set false."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/installs.py',
     'initial_latch, pruned, rule_on\n',
     'initial_latch, latch_of, pruned, rule_on\n'),
    ('ashfall_app/engine/installs.py',
     '            kept.append((p, on))\n',
     '            kept.append((p, on if p == o else latch_of(False, (False,) * len(o.unless))))\n'),
]
