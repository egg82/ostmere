"""Row 02 of MUTANTS_leaves.txt, m02: moves the shares: la's shares are added to the first share left in the mix."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/leaves.py',
     '    if len(components) == len(mix.components):\n',
     '    gone = sum(c.share_bp for c in mix.components if isinstance(c, CardShare) and c.card in cards)\n    components = tuple(replace(c, share_bp=min(10000, c.share_bp + gone)) if i == 0 and isinstance(c, CardShare) else c\n                       for i, c in enumerate(components))\n    if len(components) == len(mix.components):\n'),
]
