"""Row 18 of MUTANTS_held.txt: View.held omits the cards held at the whole share."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/view.py',
     '        held=held_views(save, rules),',
     '        held=tuple(h for h in held_views(save, rules) if h.share_bp < 10000),'),
]
