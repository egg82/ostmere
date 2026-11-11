"""Row 16 of MUTANTS_drains.txt: a store falling to its clamp at 0 is re-anchored from its rounded slope, not its
cards' work, so a split across the instant it reaches 0 rounds differently from one step."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebuild.py',
     '    if not isinstance(seg, LumpSegment):\n        return moved\n',
     '    if not isinstance(seg, LumpSegment) or seg.limit == 0:\n        return moved\n'),
]
