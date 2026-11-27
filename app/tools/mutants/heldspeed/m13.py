"""Row 13 of MUTANTS_heldspeed.txt: every lane keeps its tap's speed entries, held ones included."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    speed = tap_speed(save, rules, verb.card) if lane == HANDS else None',
     '    speed = tap_speed(save, rules, verb.card)'),
]
