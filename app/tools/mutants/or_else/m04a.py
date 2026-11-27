"""Row 04 of MUTANTS_or_else.txt: a repeating fallback tap is cancelled where the earlier action turns ready, not bounded to land at its next completion."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/retap.py',
     'from ..core.state import Save\n',
     'from ..core.state import Save\nfrom .work import interrupt as _interrupt\n'),
    ('ashfall_app/engine/orders/retap.py',
     '    whole = unit(index(rules).cards[card])\n    return _limited(',
     '    return _interrupt(save, rules, lane), True\n    whole = unit(index(rules).cards[card])\n    return _limited('),
]
