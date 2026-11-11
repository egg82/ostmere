"""Row 13 of MUTANTS_spent.txt: CardView.share_bp is served as the effective share."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/view.py',
     'share_bp=share - sum(g.share_bp for g in gained)',
     'share_bp=share'),
]
