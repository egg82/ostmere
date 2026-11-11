"""Row 10 of MUTANTS_held.txt: a greyed running mix keeps its cards' entries."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "                                if run.kind is RunKind.FULL and",
     "             if run.kind in (RunKind.FULL, RunKind.GREYED) and"),
]
