"""Row 04 of MUTANTS_groups.txt: a start of a pooled card is not refused (installs and queues still are)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/groupchecks.py',
     '    for card in (*o.starts, *(i.card for i in o.orders), *o.queues):\n',
     '    for card in (*(i.card for i in o.orders), *o.queues):\n'),
]
