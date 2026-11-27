"""Row 32 of MUTANTS.txt: entry on chainless card."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rules_check.py',
     'return any(c.id == t.card and c.chain is not None for c in rules.cards)',
     'return any(c.id == t.card for c in rules.cards)'),
]
