"""Row 22 of MUTANTS_guards.txt: too strict: a guard on a store other than the `when`'s is refused."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/decisions.py',
     '''            check_guards(rules, o.unless)
''',
     '''            check_guards(rules, o.unless)
            if any(getattr(g, "subject", None) != getattr(o.when, "subject", None) for g in o.unless):
                raise InvalidVerbError("refused")
'''),
]
