"""Row 22 of MUTANTS_guards.txt: too strict: an at-most guard is refused."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/checks.py',
     '''    for g in guards:
        check_condition(rules, g)
''',
     '''    for g in guards:
        check_condition(rules, g)
    require(not any(type(g).__name__ == "AtMost" for g in guards), "refused")
'''),
]
