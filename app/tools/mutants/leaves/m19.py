"""Row 19 of MUTANTS_leaves.txt, m19: validation: two Leaves of one lane are accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rules_check.py',
     '    check_one_leave_each(rules)\n',
     '    pass\n'),
]
