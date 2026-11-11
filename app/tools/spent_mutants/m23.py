"""Row 23 of MUTANTS_spent.txt: a spent card still runs at half its share."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     'Run(RunKind.SPENT, 0, 1, run.store)',
     'Run(RunKind.SPENT, 1, 2, run.store)'),
]
