"""Row 10 of tests/db/MUTANTS_clocks.txt: the forecast resolves an instant every minute even when nothing happens."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/forecast.py',
     'nxt = min((ev.time for ev in upcoming), default=None)',
     'nxt = min([ev.time for ev in upcoming] + [s.time + 60])'),
]
