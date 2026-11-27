"""Row 22 of MUTANTS_guards.txt: too strict: a share guard is refused."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/checks.py',
     '''    for g in guards:
        check_condition(rules, g)
''',
     '''    for g in guards:
        check_condition(rules, g)
    require(not any(getattr(g, "value_of_cap", False) or getattr(g, "release_of_cap", False) for g in guards), "refused")
'''),
]
