"""Row 05 of MUTANTS_held.txt: a * h // BP is rounded up."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))",
     "ModifierKind.ADD_BP, -(-(w.amount_bp * share) // BP), held_source(runner))"),
]
