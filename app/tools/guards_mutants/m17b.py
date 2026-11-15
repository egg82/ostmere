"""Row 17 of MUTANTS_guards.txt: past cap: a guard letting go on a mix rule past the firing cap does not wait."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/instant.py',
     '''and _moves_mix(save, event):''',
     '''and _moves_mix(save, event, rules):'''),
    ('ashfall_app/engine/instant.py',
     '''def _moves_mix(save: Save, event: Event) -> bool:
''',
     '''def _moves_mix(save: Save, event: Event, rules: Rules) -> bool:
    if not (event.kind is EventKind.LATCH and isinstance(save.orders[event.sequence].then, SwitchMix)):
        return False
    from .latches import flipped_now
    from .orders import guard_latches
    i = event.sequence
    flipped = flipped_now(save, rules, save.orders[i], save.latches[i])
    was = guard_latches(save.latches[i])
    now = guard_latches(flipped) if flipped is not None else was
    return not any(w and not n for n, w in zip(now, was))


def _moves_mix_orig(save: Save, event: Event) -> bool:
'''),
]
