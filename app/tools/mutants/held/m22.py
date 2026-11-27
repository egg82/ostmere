"""Row 22 of MUTANTS_held.txt: a tap's share is scaled by the card's bar progress, sampled at the read time."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) for c in cards}',
     '    def sampled(c: CardDef) -> int:\n        cs = next((x for x in save.cards if x.card == c.id), None)\n        return BP if cs is None else max(1, BP - cs.work.start_value % (c.work_s * BP) // c.work_s)\n    shares: dict[Runner, int] = {c.id: sampled(c) if c.id in tapped else mixed.get(c.id, 0) for c in cards}'),
]
