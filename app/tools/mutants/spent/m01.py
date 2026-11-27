"""Row 01 of MUTANTS_spent.txt: the yield follows the store, not the Pause: a hands card paused on a store that has risen
off 0 gives nothing (it is read as a receiver again) though its Pause holds until the hourly resume."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/spent.py",
     "def yielded(entries: tuple[Entry, ...], lane_of: Callable[[CardId], LaneId]\n",
     "def yielded(entries: tuple[Entry, ...], lane_of: Callable[[CardId], LaneId],\n"
     "            risen: frozenset[CardId] = frozenset()\n"),
    ("ashfall_app/engine/spent.py",
     "        given = [(card, share) for card, share, run in on if run.kind in GIVES]\n"
     "        rest = [(card, share) for card, share, run in on if run.kind not in GIVES]\n",
     "        given = [(card, share) for card, share, run in on if run.kind in GIVES and card not in risen]\n"
     "        rest = [(card, share) for card, share, run in on if run.kind not in GIVES or card in risen]\n"),
    ("ashfall_app/engine/mixruns.py",
     "    return yielded(entries, lambda _: HANDS)\n",
     "    risen = frozenset(c for c, _, run in entries if run.kind is RunKind.PAUSED and next(\n"
     "        st.segment.start_value for st in save.stores if st.store == run.store) > 0)\n"
     "    return yielded(entries, lambda _: HANDS, risen)\n"),
]
