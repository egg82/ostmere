"""Row 08 of MUTANTS_heldspeed.txt: a resume does not rebuild."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '    return rebuild(replace(save, pauses=tuple(p for p in save.pauses if p.runner != runner)), rules)',
     '    return replace(save, pauses=tuple(p for p in save.pauses if p.runner != runner))'),
]
