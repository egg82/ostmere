"""Row 12 of MUTANTS.txt: leaving."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/leaves.py',
     '    unlocked = tuple(sorted({*save.unlocked, Unlock(UnlockKind.LEFT, leave.lane)}, key=unlock_key))\n',
     "    unlocked = tuple(sorted({*(u for u in save.unlocked if not (u.kind is UnlockKind.FEATURE and u.id.endswith('_' + leave.lane))), Unlock(UnlockKind.LEFT, leave.lane)}, key=unlock_key))\n"),
]
