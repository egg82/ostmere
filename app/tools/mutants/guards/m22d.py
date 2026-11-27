"""Row 22 of MUTANTS_guards.txt: too strict: a guard on a mix rule is refused."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '''            check_guards(rules, o.unless)
''',
     '''            check_guards(rules, o.unless)
            if isinstance(o.then, SwitchMix) and o.unless:
                raise InvalidVerbError("refused")
'''),
]
