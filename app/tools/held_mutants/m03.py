"""Row 3 of MUTANTS_held.txt: the entry lands on ThreatStrength instead of SideStrength."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     'from .modifiers import LaneSpeed, Modifier, ModifierKind, RunKind, SideStrength',
     'from .modifiers import LaneSpeed, Modifier, ModifierKind, RunKind, SideStrength, ThreatStrength'),
    ('ashfall_app/engine/heldentries.py',
     'else SideStrength(w.side)',
     'else ThreatStrength(w.side)'),
]
