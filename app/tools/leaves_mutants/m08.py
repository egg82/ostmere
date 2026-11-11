"""Row 08 of MUTANTS_leaves.txt, m08: too many orders: a leave removes every order whose verb is a tap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     'from .installs import without_taps\n',
     'from .installs import without_taps\nfrom .lanes import TapCard\n'),
    ('ashfall_app/engine/leaves.py',
     '    save = without_taps(replace(save, unlocked=unlocked), cards)\n',
     '    save = without_taps(replace(save, unlocked=unlocked), frozenset(\n        o.then.card for o in save.orders if isinstance(o.then, TapCard)))\n'),
]
