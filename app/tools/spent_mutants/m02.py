"""Row 02 of MUTANTS_spent.txt: the town mix's yield crosses lanes, one person's spent share going to another's cards."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/mixruns.py", "    return yielded(entries, lambda card: cards[card].lane)\n",
     "    return yielded(entries, lambda _: HANDS)\n"),
]
