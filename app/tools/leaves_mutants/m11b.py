"""Row 11 of MUTANTS_leaves.txt, m11b: still listed: a left lane stays in View.lanes."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/view.py',
     '        if not _lane_shown(save, rules, ls.lane) or is_left(save, ls.lane):\n',
     '        if not _lane_shown(save, rules, ls.lane):\n'),
]
