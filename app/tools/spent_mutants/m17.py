"""Row 17 of MUTANTS_spent.txt: explain() never lists `gained`."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/api.py',
     '    return replace(e, gained=gained) if gained else e\n',
     '    return e\n'),
]
