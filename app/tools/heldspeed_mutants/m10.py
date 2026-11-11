"""Row 10 of MUTANTS_heldspeed.txt: View.held lists standing holders first."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/view.py',
     '        held=held_views(save, rules),',
     '        held=tuple(sorted(held_views(save, rules), key=lambda h: h.card not in {a.id for a in rules.standing})),'),
]
