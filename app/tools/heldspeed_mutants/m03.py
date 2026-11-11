"""Row 03 of MUTANTS_heldspeed.txt: a HeldSpeed lands on HANDS."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    target = LaneSpeed(w.lane) if isinstance(w, HeldSpeed)',
     '    target = LaneSpeed(LaneId("hands")) if isinstance(w, HeldSpeed)'),
    ('ashfall_app/engine/heldentries.py',
     'from .ids import CardId, Runner, SourceId',
     'from .ids import CardId, LaneId, Runner, SourceId'),
]
