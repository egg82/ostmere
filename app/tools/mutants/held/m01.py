"""Row 01 of MUTANTS_held.txt: the entry is held at its whole amount_bp whatever h(c) is."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "ModifierKind.ADD_BP, w.amount_bp * share // BP, held_source(runner))",
     "ModifierKind.ADD_BP, w.amount_bp, held_source(runner))"),
]
