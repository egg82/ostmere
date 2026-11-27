"""Row 10 of MUTANTS.txt: left."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/casts.py',
     '    running = [p for p in c.picks if is_joined(save, rules, p.lane) and not is_left(save, p.lane)\n',
     '    running = [p for p in c.picks if is_joined(save, rules, p.lane)\n'),
]
