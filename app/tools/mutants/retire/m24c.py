"""Row 24 of MUTANTS_leaves.txt, m24c: logs nothing: the level of a removed order is dropped."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rulelog.py',
     '            found.append(RuleChange(after.time, o, False, _level(after, rules, o), why))\n',
     '            found.append(RuleChange(after.time, o, False, None, why))\n'),
]
