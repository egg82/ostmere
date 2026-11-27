"""Row 09 of MUTANTS_leaves.txt, m09: LEFT unwritten: Unlock(LEFT) is never added."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    unlocked = tuple(sorted({*save.unlocked, Unlock(UnlockKind.LEFT, leave.lane)}, key=unlock_key))\n',
     '    unlocked = save.unlocked\n'),
]
