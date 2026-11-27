"""Row 01 of MUTANTS_drains.txt: a drain treated as an input: no forgiveness at 0, and the dry rule pauses its card like any consumer."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebuild.py',
     '    if (flow == 0 and not moving[1]) or (v == 0 and forgiven(rules, d.id, flow, terms, work)):\n',
     '    if flow == 0 and not moving[1]:\n'),
    ('ashfall_app/engine/handlers.py',
     '        paused = {p.runner for p in save.pauses} | set(landing) | drainers(rules, store)\n',
     '        paused = {p.runner for p in save.pauses} | set(landing)\n'),
]
