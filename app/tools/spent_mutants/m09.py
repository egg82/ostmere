"""Row 09 of MUTANTS_spent.txt: each receiver floors the sum of its gains once and names the first spent card as its source."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/spent.py',
     'for k, s_k in given if (g := s_k * share // total) > 0)',
     'for k, s_k in given[:1] if (g := sum(s for _, s in given) * share // total) > 0)'),
]
