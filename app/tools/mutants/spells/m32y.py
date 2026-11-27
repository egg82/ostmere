"""Row 32 of MUTANTS.txt: entry on unknown card."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/rules_check.py',
     'return any(c.id == t.card and c.chain is not None for c in rules.cards)',
     'return True'),
]
