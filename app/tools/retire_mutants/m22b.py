"""Row 22 of MUTANTS_leaves.txt, m22b: retires partly: the latches shift, so a kept order takes a removed one's."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/installs.py',
     '    return replace(save, orders=tuple(o for o, _ in kept), latches=tuple(on for _, on in kept))\n',
     '    return replace(save, orders=tuple(o for o, _ in kept), latches=save.latches[:len(kept)])\n'),
]
