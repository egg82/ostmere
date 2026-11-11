"""Row 23 of MUTANTS_held.txt: the lock counts while_running as part of a released card: a card that gains it reads as having a lower cap in the lock's snapshot."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/opening/lock.py",
     "card_caps={c.id: c.cap for c in rules.cards},",
     "card_caps={c.id: (c.cap if not c.while_running else 0) for c in rules.cards},"),
]
