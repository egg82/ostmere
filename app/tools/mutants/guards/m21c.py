"""Row 21 of MUTANTS_guards.txt: limits: a guard that reads lane rules is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    for g in guards:
        check_condition(rules, g)
''',
     '''    for g in guards:
        problem = condition_problem(rules, g)
        require(problem is None, problem or "")
'''),
]
