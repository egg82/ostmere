"""Row 08 of MUTANTS_or_else.txt: candidates (the READY events) list only each rule's `then`."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/plan.py',
     '    verbs = [a for _, a, latch in listed(save.orders, save.latches) if rule_on(latch)]\n',
     '    verbs = [a for i, a, latch in listed(save.orders, save.latches) if rule_on(latch) and a == save.orders[i].then]\n'),
]
