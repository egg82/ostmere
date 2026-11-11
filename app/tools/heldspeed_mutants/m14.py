"""Row 14 of MUTANTS_heldspeed.txt: a ceiling."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    return Modifier(target, ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))',
     '    return Modifier(target, ModifierKind.ADD_BP, -(-(w.amount_bp * share) // BP), held_source(runner))'),
]
