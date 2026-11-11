"""Row 17 of MUTANTS_held.txt: the held entry is sourced by the bare card id."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    return SourceId(f"{HELD_PREFIX}{runner}")',
     '    return SourceId(f"{runner}")'),
]
