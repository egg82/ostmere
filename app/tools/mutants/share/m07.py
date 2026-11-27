"""Row 07 of MUTANTS_share.txt: cap at start."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/sharelevels.py',
     '    whole = store_cap(save, rules, cond.subject.store) // Q\n',
     '    whole = next(d.cap for d in rules.stores if d.id == cond.subject.store) // Q\n'),
]
