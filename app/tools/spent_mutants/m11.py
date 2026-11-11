"""Row 11 of MUTANTS_spent.txt: a locked, completed or retired card counts as a maker."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     '    if not is_unlocked(save, rules, u):\n        return False\n    return u.kind is not UnlockKind.CARD or not is_completed(save, rules, CardId(runner))\n',
     '    return True\n'),
]
