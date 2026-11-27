"""Row 09 of MUTANTS_held.txt: a mix card waiting on a false requires keeps its entry."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "                                if run.kind is RunKind.FULL and",
     "             if run.kind in (RunKind.FULL, RunKind.WAITING) and"),
]
