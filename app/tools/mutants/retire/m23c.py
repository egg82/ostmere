"""Row 23 of MUTANTS_leaves.txt, m23c: touches the rest: the turn also clears the unlocks."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    save = left(without_taps(save, o.retire_orders), rules, o.leaves)\n',
     '    save = left(replace(without_taps(save, o.retire_orders), unlocked=()) if o.retire_orders else save, rules, o.leaves)\n'),
]
