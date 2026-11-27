"""Row 07 of MUTANTS.txt: revived."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/casts.py',
     '    for i in range(len(c.picks[0].counted) if c.picks else 0):\n',
     '    everyone = list(running)\n    for i in range(len(c.picks[0].counted) if c.picks else 0):\n'),
    ('ashfall_app/engine/people/casts.py',
     '        counts = [(_count(save, rules, p, i), p) for p in running]\n',
     '        counts = [(_count(save, rules, p, i), p) for p in everyone]\n'),
]
