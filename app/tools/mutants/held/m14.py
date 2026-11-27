"""Row 14 of MUTANTS_held.txt: the entries are written into save.modifiers by rebuild and the stack no longer adds them."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/unlocks/gates.py',
     '    return save.modifiers + chip_modifiers(save, rules) + held_entries(save, rules)',
     '    return save.modifiers + chip_modifiers(save, rules)'),
    ('ashfall_app/engine/loop/rebuild.py',
     '    rebuilt = replace(save, stores=stores, skills=skills, cards=cards)\n',
     '    from ..modifiers.heldentries import held_entries\n    from ..cards.cards import HELD_PREFIX\n    kept = tuple(m for m in save.modifiers if not str(m.source).startswith(HELD_PREFIX))\n    rebuilt = replace(save, stores=stores, skills=skills, cards=cards, modifiers=kept + held_entries(save, rules))\n'),
]
