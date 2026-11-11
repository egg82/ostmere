"""Row 16 of MUTANTS_leaves.txt, m16: rebase misses it: a leave landed at the rebase instant is not logged."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebase.py',
     '    return Step(after, numbered(lines), rule_changes=rule_changes(before, after, rules))\n',
     '    return Step(after, numbered(lines), rule_changes=())\n'),
]
