"""Row 03 of MUTANTS_heldspeed.txt: a HeldSpeed lands on HANDS."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/modifiers/heldentries.py',
     '    target = LaneSpeed(w.lane) if isinstance(w, HeldSpeed)',
     '    target = LaneSpeed(LaneId("hands")) if isinstance(w, HeldSpeed)'),
    ('ashfall_app/engine/modifiers/heldentries.py',
     'from ..core.ids import CardId, Runner, SourceId',
     'from ..core.ids import CardId, LaneId, Runner, SourceId'),
]
