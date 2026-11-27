"""Row 05 of MUTANTS_share.txt: exact cap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/sharelevels.py',
     '    whole = store_cap(save, rules, cond.subject.store) // Q\n',
     '    whole = store_cap(save, rules, cond.subject.store) / Q\n'),
]
