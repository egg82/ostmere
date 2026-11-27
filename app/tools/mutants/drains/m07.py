"""Row 07 of MUTANTS_drains.txt: a tap takes min(x, A') at its start instant."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    return rebuild(replace(save, lanes=occupied, cards=stilled), rules)\n',
     '    took = {a.store: min(store_value(save, a.store), a.quantity) for a in index(rules).cards[verb.card].drains}\n    lumped = tuple(StoreState(st.store, Segment(save.time, st.segment.start_value - took[st.store], 0))\n                   if st.store in took else st for st in save.stores)\n    return rebuild(replace(save, lanes=occupied, cards=stilled, stores=lumped), rules)\n'),
]
