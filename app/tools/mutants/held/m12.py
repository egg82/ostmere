"""Row 12 of MUTANTS_held.txt: a card with work in progress keeps its entry (kept work read as presence), so an interrupted task still holds."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     'from .index import derived',
     'from .index import derived, index'),
    ('ashfall_app/engine/heldentries.py',
     '    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) for c in cards}',
     '    tapped |= {cs.card for cs in save.cards if cs.work.start_value % (index(rules).cards[cs.card].work_s * BP)}\n    shares: dict[Runner, int] = {c.id: BP if c.id in tapped else mixed.get(c.id, 0) for c in cards}'),
]
