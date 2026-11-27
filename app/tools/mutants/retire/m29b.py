"""Row 29 of MUTANTS_leaves.txt, m29b: rebase misses it: a trigger new to the save is taken as fired, so no turn lands at the rebase."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebase.py',
     '        fired=tuple(fired.get(x.id, False) for x in rules.triggers),\n',
     '        fired=tuple(fired.get(x.id, True) for x in rules.triggers),\n'),
]
