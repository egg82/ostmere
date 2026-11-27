"""Row 14 of MUTANTS.txt: rebase drops."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/unlock_known.py',
     '    found[UnlockKind.FEATURE] |= {f for fs in cast_features(rules).values() for f in fs}\n',
     '    pass\n'),
]
