"""Row 38 of MUTANTS.txt: chain not served."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/goals/fight_infos.py',
     '    if c.chain is None:\n        return None\n',
     '    if True:\n        return None\n'),
]
