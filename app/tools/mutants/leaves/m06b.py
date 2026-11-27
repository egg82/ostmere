"""Row 06 of MUTANTS_leaves.txt, m06b: logs wrongly: the removed orders' level is read from the save before the instant."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rulelog.py',
     '            found.append(RuleChange(after.time, o, False, _level(after, rules, o), why))\n',
     '            found.append(RuleChange(after.time, o, False, _level(before, rules, o), why))\n'),
]
