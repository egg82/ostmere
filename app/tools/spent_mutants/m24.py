"""Row 24 of MUTANTS_spent.txt: a card paused on a spent store reads YIELDED during a hands tap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/mixruns.py',
     '    if paused_on is not None:\n        return Run(RunKind.PAUSED, 0, 1, paused_on)\n',
     '    if handed:\n        return Run(RunKind.YIELDED, 0, 1)\n    if paused_on is not None:\n        return Run(RunKind.PAUSED, 0, 1, paused_on)\n'),
]
