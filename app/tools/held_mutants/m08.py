"""Row 08 of MUTANTS_held.txt: a mix card paused on a dry store keeps its entry."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "                                if run.kind is RunKind.FULL and",
     "             if run.kind in (RunKind.FULL, RunKind.PAUSED) and"),
]
