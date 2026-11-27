"""Row 15 of MUTANTS_spent.txt: a card counts as a maker only while it occupies a lane, so an unlocked card nobody taps is no maker."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     '    return u.kind is not UnlockKind.CARD or not is_completed(save, rules, CardId(runner))\n',
     '    return u.kind is not UnlockKind.CARD or (not is_completed(save, rules, CardId(runner))\n                                             and any(ls.card == runner for ls in save.lanes))\n'),
]
