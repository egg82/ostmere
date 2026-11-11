"""Row 04 of MUTANTS_drains.txt: a forgiven store at 0 rises (the drain adds)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebuild.py',
     '    if (flow == 0 and not moving[1]) or (v == 0 and forgiven(rules, d.id, flow, terms, work)):\n        return Segment(save.time, v, 0)\n',
     '    if v == 0 and forgiven(rules, d.id, flow, terms, work):\n        return Segment(save.time, v, 1)\n    if flow == 0 and not moving[1]:\n        return Segment(save.time, v, 0)\n'),
]
