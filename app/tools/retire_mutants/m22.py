"""Row 22 of MUTANTS_leaves.txt, m22: retires partly: only the first matching order goes."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/installs.py',
     '    kept = [(o, on) for o, on in zip(save.orders, save.latches)\n            if not (isinstance(o.then, TapCard) and o.then.card in cards)]\n',
     '    first = next((i for i, o in enumerate(save.orders) if isinstance(o.then, TapCard) and o.then.card in cards), -1)\n    kept = [(o, on) for i, (o, on) in enumerate(zip(save.orders, save.latches)) if i != first]\n'),
]
