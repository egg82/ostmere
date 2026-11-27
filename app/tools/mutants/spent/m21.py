"""Row 21 of MUTANTS_spent.txt: a card reached through a sub-mix as well as directly is read at its first share."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/mixes.py", "                acc[card] = acc.get(card, 0) + share * c.share_bp // BP\n",
     "                acc.setdefault(card, share * c.share_bp // BP)\n"),
]
