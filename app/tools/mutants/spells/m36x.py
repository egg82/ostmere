"""Row 36 of MUTANTS.txt: locked card listed."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     '                 if c.chain is not None and is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id))\n',
     '                 if c.chain is not None\n'),
]
