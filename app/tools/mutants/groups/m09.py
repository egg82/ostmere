"""Row 09 of MUTANTS_groups.txt: a lane's own_split is written into every save's encoding, at its default too."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/savefile/codec.py',
     '("Join", "own_split"): True,\n    ("LaneState", "own_split"): True}',
     '("Join", "own_split"): True}'),
]
