"""Row 11 of MUTANTS_guards.txt: start cap: the view reads the quantity a share guard lets go at off the starting cap."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/read/view.py',
     '''        return read_levels(save, rules, cond).release
''',
     '''        if cond.value_of_cap or cond.release_of_cap:
            whole = next(s.cap for s in rules.stores if s.id == cond.subject.store) // QUANTITY_SCALE
            from dataclasses import replace as _r
            return read_levels(save, _r(rules, stores=tuple(_r(s, cap=whole * QUANTITY_SCALE) for s in rules.stores)), cond).release
        return read_levels(save, rules, cond).release
'''),
]
