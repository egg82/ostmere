"""Row 15 of MUTANTS_held.txt: the share is floored twice (to 100ths, then the amount)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     'ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))',
     'ModifierKind.ADD_BP, w.amount_bp * (share // 100) // 100, held_source(runner))'),
]
