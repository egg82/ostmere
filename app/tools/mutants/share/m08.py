"""Row 08 of MUTANTS_share.txt: in content."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/rules_check.py',
     '        return "a share level is a saved rule\'s alone" if in_rules else share_problem(cond)\n',
     '        return share_problem(cond)\n'),
]
