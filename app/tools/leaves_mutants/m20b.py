"""Row 20 of MUTANTS_leaves.txt, m20b: explanations move: a leave clears every pause, not only those of la's cards and the stops."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '                   pauses=tuple(p for p in save.pauses if p.runner not in runners))\n',
     '                   pauses=())\n'),
]
