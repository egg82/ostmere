"""Row 13 of MUTANTS_held.txt: h(c) reads save.active instead of the running mix."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    mixed: dict[CardId, int] = {card: share for card, share, run in (*mix_entries(save, rules), *town_entries(save, rules))',
     '    from .mixes import flatten_shares\n    from .mixruns import _entries\n    act = () if save.active is None else _entries(save, rules, flatten_shares(save.mixes, save.active), save.active, lambda _: False)\n    mixed: dict[CardId, int] = {card: share for card, share, run in (*act, *town_entries(save, rules))'),
]
