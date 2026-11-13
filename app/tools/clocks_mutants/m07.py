"""Row 07 of tests/db/MUTANTS_clocks.txt: a claim ignores an earlier send, so two jobs both win."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/db/reminders.py',
     'rd.c.id == device_id, rd.c.visited_at == visited_at,\n        or_(rd.c.last_sent_at.is_(None), rd.c.last_sent_at < rd.c.visited_at))',
     'rd.c.id == device_id, rd.c.visited_at == visited_at)'),
]
