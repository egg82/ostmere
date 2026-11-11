"""Row 07 of MUTANTS_heldspeed.txt: a pause at the instant is not rebuilt before the next is picked, so the store reads
dry under the stack from before the pause and every eater pauses where one suffices."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '        save = rebuild(replace(save, pauses=pauses), rules)\n        lane = _tapped_lane(save, rules, a)\n',
     '        save = replace(save, pauses=pauses)\n        lane = _tapped_lane(save, rules, a)\n'),
]
