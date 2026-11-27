"""Row 14 of MUTANTS_spent.txt: a paused card on a spent store still makes its ledger line starved."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    if paused and any(running(save, rules).runs.get(r, FULL).kind is not RunKind.SPENT for r in paused):\n',
     '    if paused:\n'),
]
