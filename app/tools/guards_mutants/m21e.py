"""Row 21 of MUTANTS_guards.txt: limits: a guard whose release is on the wrong side of its value is accepted (a latch that never settles; the instant's settle bound is lowered so it fails, not hangs)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/checks.py',
     '''    for g in guards:
        check_condition(rules, g)
''',
     '''    for g in guards:
        problem = condition_problem(rules, g)
        require(problem is None or "wrong side" in problem, problem or "")
        require(not is_lane_rules(g), "a lane-rules condition is only a trigger's")
'''),
    ('ashfall_app/engine/instant.py',
     '''_SETTLE_GUARD = 1_000_000
''',
     '''_SETTLE_GUARD = 3_000
'''),
]
