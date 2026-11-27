"""Row 17 of MUTANTS_drains.txt: CardView.needs lists a drain's store."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/read/view.py',
     '    want: dict[StoreId, int] = {s: q for s, q in input_whole(save, rules, c) if q > 0}\n',
     '    want: dict[StoreId, int] = {s: q for s, q in input_whole(save, rules, c) if q > 0}\n    want |= {a.store: 1 for a in c.drains}\n'),
]
