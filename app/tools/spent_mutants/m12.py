"""Row 12 of MUTANTS_spent.txt: the yield lags the pool's emptying: the store's limit event, where the dry rule pauses the
card and the yield starts, is handled one second after the store reaches 0."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/schedule.py", "                found.append(Event(t, EventKind.STORE_LIMIT, i, st.store))\n",
     "                found.append(Event(t + 1, EventKind.STORE_LIMIT, i, st.store))\n"),
]
