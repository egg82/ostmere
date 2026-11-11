"""Row 21 of MUTANTS_held.txt: the held shares are cached by lanes and mixes only, so a pause at the instant does not show in the next pick."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    return _SHARES.get(save, rules, lambda: _held_cards(save, rules))',
     '    key = (id(rules), save.time, save.lanes, save.mixes, save.active, save.orders, save.latches, save.unlocked)\n    if key not in _STALE:\n        _STALE[key] = _held_cards(save, rules)\n    return _STALE[key]\n\n\n_STALE: dict[object, dict[CardId, int]] = {}'),
]
