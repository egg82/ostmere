"""Row 07 of MUTANTS_groups.txt: a mark's card may be a capped card or one off the lane."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/groupchecks.py',
     '    if m.card is not None and (m.card not in on_lane or m.card in capped):\n',
     '    if False:\n'),
]
