"""Row 07 of MUTANTS_spent.txt: the yield reaches the save: a receiver's Pause takes its resume level from its effective
share, so equal saves can carry different Pauses and a re-decoded save runs differently."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/handlers.py", "        saved = now.shares[a] - sum(g.share_bp for g in now.gained.get(a, ()))\n",
     "        saved = now.shares[a]\n"),
]
