"""Row 29 of MUTANTS_leaves.txt, m29: rebase misses it: the orders removed at a turn already past are not logged."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebase.py',
     '    return Step(after, numbered(lines), rule_changes=rule_changes(before, after, rules), dropped=gone.counts())\n',
     '    return Step(after, numbered(lines), rule_changes=(), dropped=gone.counts())\n'),
]
