"""Row 03 of MUTANTS_spent.txt: a town mix's cards and a hands mix's cards are yielded together, so a spent hands card gives to the town mix."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/mixruns.py',
     '    return yielded(entries, lambda card: cards[card].lane)\n',
     '    return yielded(entries + _MIX.get(save, rules, lambda: _mix_entries(save, rules))[0], lambda _: HANDS)\n'),
]
