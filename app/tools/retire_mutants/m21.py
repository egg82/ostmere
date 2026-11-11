"""Row 21 of MUTANTS_leaves.txt, m21: retires others: the turn removes the orders tapping any card on the named cards' lanes."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    save = left(without_taps(save, o.retire_orders), rules, o.leaves)\n',
     '    save = left(without_taps(save, frozenset(c.id for c in rules.cards if c.lane in {\n        x.lane for x in rules.cards if x.id in o.retire_orders})), rules, o.leaves)\n'),
]
