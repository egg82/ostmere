"""Row 03 of MUTANTS.txt: total."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/casts.py',
     '    return 0 if card is None else completions(save, rules, card)\n',
     '    return 0 if card is None else sum(completions(save, rules, c.id) for c in rules.cards if c.id.endswith(card[len(pick.lane):]))\n'),
]
