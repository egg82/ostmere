"""Row 07 of MUTANTS_held.txt: a card tapped while in the running mix holds BP plus its mix share (the mix share of a yielded card is read too)."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "                                if run.kind is RunKind.FULL and",
     "                                if run.kind in (RunKind.FULL, RunKind.YIELDED) and"),
    ("ashfall_app/engine/heldentries.py", "    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) for c in cards}",
     "    shares: dict[Runner, int] = {c.id: (BP if c.id in tapped else 0) + mixed.get(c.id, 0) for c in cards}"),
]
