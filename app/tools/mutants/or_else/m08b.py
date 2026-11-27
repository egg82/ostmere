"""Row 08 of MUTANTS_or_else.txt: watch_events (READY while a lane repeats) read only each rule's `then`."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/retap.py',
     '        for _, verb, latch in listed(save.orders, save.latches):\n            if not rule_on(latch) or not isinstance(verb, TapCard):\n',
     '        for i, verb, latch in listed(save.orders, save.latches):\n            if not rule_on(latch) or not isinstance(verb, TapCard) or verb != save.orders[i].then:\n'),
]
