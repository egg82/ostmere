"""Row 05 of MUTANTS_groups.txt: a mark is allowed in any outcome, a card's included."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/groupchecks.py',
     '        if not once_only:\n',
     '        if False:\n'),
]
