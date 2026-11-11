"""Row 11 of MUTANTS_leaves.txt, m11: still listed: a left card stays in View.cards and View.completed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/view.py',
     ' and not is_left(save, c.lane)]',
     ']'),
]
