"""Row 06 of MUTANTS_held.txt: a share keeps its entry while a tap holds its lane."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/heldentries.py", "                                if run.kind is RunKind.FULL and",
     "                                if run.kind in (RunKind.FULL, RunKind.YIELDED) and"),
]
