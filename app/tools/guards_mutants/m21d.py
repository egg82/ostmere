"""Row 21 of MUTANTS_guards.txt: limits: a guard whose share level is invalid (over BP, of a skill) is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/checks.py',
     '''    for g in guards:
        check_condition(rules, g)
''',
     '''    for g in guards:
        problem = condition_problem(rules, g)
        require(problem is None or problem.startswith("a share level"), problem or "")
        require(not is_lane_rules(g), "a lane-rules condition is only a trigger's")
'''),
]
