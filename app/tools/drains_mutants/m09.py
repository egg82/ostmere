"""Row 09 of MUTANTS_drains.txt: the dry rule skips a store that has a drain on it."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '    interrupted, built = False, True\n    dry = _dry(save, store)\n',
     '    interrupted, built = False, True\n    dry = _dry(save, store) and not drainers(rules, store)\n'),
]
