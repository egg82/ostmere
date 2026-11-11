"""Row 24 of MUTANTS_held.txt: rebase writes the held entries of the rebased save into its modifiers."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebase.py',
     '    return shaped, resolve_instant(rebuild(shaped, rules), rules, [], True, emit)',
     '    from .heldentries import held_entries\n    shaped = replace(shaped, modifiers=shaped.modifiers + held_entries(shaped, rules))\n    return shaped, resolve_instant(rebuild(shaped, rules), rules, [], True, emit)'),
]
