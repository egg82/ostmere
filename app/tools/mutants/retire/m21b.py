"""Row 21 of MUTANTS_leaves.txt, m21b: retires others: the turn removes the orders tapping any card making a store a named card makes."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    save = left(without_taps(save, o.retire_orders), rules, o.leaves)\n',
     '    save = left(without_taps(save, frozenset(c.id for c in rules.cards if {f.store for f in c.makes} & {\n        f.store for x in rules.cards if x.id in o.retire_orders for f in x.makes})), rules, o.leaves)\n'),
]
