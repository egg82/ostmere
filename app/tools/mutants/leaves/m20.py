"""Row 20 of MUTANTS_leaves.txt, m20: explanations move: the shares left in a mix are halved by the leave."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    if len(components) == len(mix.components):\n',
     '    components = tuple(replace(c, share_bp=c.share_bp // 2) if isinstance(c, CardShare) else c for c in components)\n    if len(components) == len(mix.components):\n'),
]
