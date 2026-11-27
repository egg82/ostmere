"""Row 02 of MUTANTS_spent.txt: the town mix's yield crosses lanes, one person's spent share going to another's cards."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/mixes/mixruns.py", "    return crewed(save, rules, *yielded(entries, lambda card: cards[card].lane))\n",
     "    return crewed(save, rules, *yielded(entries, lambda _: HANDS))\n"),
]
