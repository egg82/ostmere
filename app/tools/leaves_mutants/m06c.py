"""Row 06 of MUTANTS_leaves.txt, m06c: logs wrongly: every removed order is logged twice."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rulelog.py',
     '            found.append(RuleChange(after.time, o, False, _level(after, rules, o), why))\n',
     '            found.append(RuleChange(after.time, o, False, _level(after, rules, o), why))\n            found.append(RuleChange(after.time, o, False, _level(after, rules, o), why))\n'),
]
