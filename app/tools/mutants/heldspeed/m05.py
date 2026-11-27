"""Row 05 of MUTANTS_heldspeed.txt: a multiplier of BP + amount."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    return Modifier(target, ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))',
     '    if isinstance(w, HeldSpeed):\n        return Modifier(target, ModifierKind.MUL_BP, BP + w.amount_bp * share // BP, held_source(runner))\n    return Modifier(target, ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))'),
]
