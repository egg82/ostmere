"""Row 05 of MUTANTS_spent.txt: no fixpoint: a store is spent only when no maker is in play, so one whose every maker
takes from an empty spent store is not."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/spent.py", "            if any(not (takes & blocked) for takes in live.get(x, ())):\n",
     "            if live.get(x):\n"),
]
