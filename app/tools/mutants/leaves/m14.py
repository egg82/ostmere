"""Row 14 of MUTANTS_leaves.txt, m14: locks the action: Unlocked(ACTION) of a stopped standing action reads false."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/unlocked.py',
     '    if rules.opening is None and u.kind not in PRESENT_ONLY:\n        return True\n',
     '    from .gone import stopped\n    if u.kind.value == "action" and u.id in stopped(save, rules):\n        return False\n    if rules.opening is None and u.kind not in PRESENT_ONLY:\n        return True\n'),
]
