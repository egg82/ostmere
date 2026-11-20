"""Row 07 of MUTANTS_heldspeed.txt: the store's net after a pause is read under the stack from before the pause, so
the store reads dry and every eater pauses where one suffices."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '        rate = None if lane is not None else store_rate(save, rules, store)\n',
     '        rate = None if lane is not None else store_rate(replace(save, pauses=tuple(p for p in pauses if p.runner != a)),'
     ' rules, store)\n'),
    ('ashfall_app/engine/handlers.py',
     '            dry = _dry(save, store)\n',
     '            dry = _dry(rebuild(replace(save, pauses=tuple(p for p in save.pauses if p.runner != a)), rules), store)\n'),
]
