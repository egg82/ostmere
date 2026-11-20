"""Row 11 of MUTANTS_groups.txt: a group card's share is not multiplied by its free members."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/groups.py',
     '        return card, share * free, run\n',
     '        return card, share, run\n'),
]
