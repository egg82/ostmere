"""Row 22 of MUTANTS_leaves.txt, m22: retires partly: only the first matching order goes."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/installs.py',
     '    kept: list[tuple[Order, Latch]] = []\n    for o, on in zip(save.orders, save.latches):\n        p = pruned(o, lambda a, o=o: drop(o, a))\n',
     '    kept: list[tuple[Order, Latch]] = []\n    done = False\n    for o, on in zip(save.orders, save.latches):\n        p = o if done else pruned(o, lambda a, o=o: drop(o, a))\n        done = done or p != o\n'),
]
