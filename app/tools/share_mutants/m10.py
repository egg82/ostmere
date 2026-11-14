"""Row 10 of MUTANTS_share.txt: latch unread."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/decisions.py',
     '    return initial_latch(read_levels(save, rules, cond), subject_value(save, rules, cond.subject), save.time)\n',
     '    return initial_latch(cond, subject_value(save, rules, cond.subject), save.time)\n'),
]
