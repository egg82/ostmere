"""Row 08 of MUTANTS_spent.txt: the proportion is over the receivers' running shares: a waiting receiver is left out of Rsum."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     'if run.kind not in GIVES]\n        total',
     'if run.kind not in GIVES | {RunKind.WAITING}]\n        total'),
]
