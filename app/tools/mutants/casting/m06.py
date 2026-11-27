"""Row 06 of MUTANTS.txt: summed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/casts.py',
     '        counts = [(_count(save, rules, p, i), p) for p in running]\n',
     '        counts = [(sum(_count(save, rules, p, j) for j in range(len(p.counted))), p) for p in running]\n'),
]
