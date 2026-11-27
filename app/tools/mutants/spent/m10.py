"""Row 10 of MUTANTS_spent.txt: a trigger whose outcome adds to a store counts as a maker of it, so a pool with a turn coming is never spent."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     '    spent = {d.id for d in rules.stores}\n',
     '    spent = {d.id for d in rules.stores} - {a.store for t in rules.triggers for a in t.outcome.stores}\n'),
]
