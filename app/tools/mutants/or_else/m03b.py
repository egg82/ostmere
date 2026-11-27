"""Row 03 of MUTANTS_or_else.txt: a repeating (rate) tap holds while any true rule lists it, so a fallback run as a rate never yields."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '    return controlling_verb(_freed(save, lane), rules) == TapCard(card)\n',
     '    return controlling_verb(_freed(save, lane), rules) == TapCard(card) or any(rule_on(l) and a == TapCard(card) for _, a, l in listed(save.orders, save.latches))\n'),
    ('ashfall_app/engine/loop/instant.py',
     '_SETTLE_GUARD = 1_000_000\n',
     '_SETTLE_GUARD = 3_000\n'),
]
