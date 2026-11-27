"""Row 04 of MUTANTS_heldspeed.txt: rate lines skip a held lane speed; only work reads it."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rates.py',
     '    return tuple(replace(m, target=ref) for m in _picked(save, rules, [ref], speed, run))',
     '    return tuple(replace(m, target=ref) for m in _picked(save, rules, [ref], speed, run)\n                 if not (str(m.source).startswith("held:") and isinstance(m.target, LaneSpeed)))'),
]
