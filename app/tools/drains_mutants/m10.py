"""Row 10 of MUTANTS_drains.txt: the dry rule counts the drain in its net (no forgiveness in the store's segment at 0)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebuild.py',
     '    if (flow == 0 and not moving[1]) or (v == 0 and forgiven(rules, d.id, flow, terms, work)):\n',
     '    if flow == 0 and not moving[1]:\n'),
]
