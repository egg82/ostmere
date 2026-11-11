"""Row 04 of MUTANTS_held.txt: the entry is held while the card is unlocked, running or not."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) for c in cards}",
     "    unlocked = {c.id for c in cards if is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id))}\n    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) or (BP if c.id in unlocked else 0) for c in cards}"),
]
