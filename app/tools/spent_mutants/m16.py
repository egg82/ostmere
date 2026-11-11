"""Row 16 of MUTANTS_spent.txt: a card's costs are not takes, only its inputs."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     'frozenset(f.store for f in c.costs) | frozenset(\n',
     'frozenset(\n'),
]
