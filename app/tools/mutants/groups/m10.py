"""Row 10 of MUTANTS_groups.txt: the lane bar shows a mark on a pooled lane, which is no person."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/view.py',
     'ls.lane in ix.ruled and ls.lane not in ix.pooled else None',
     'ls.lane in ix.ruled else None'),
]
