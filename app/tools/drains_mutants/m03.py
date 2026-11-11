"""Row 03 of MUTANTS_drains.txt: no clamp at 0 on a drained store: its falling segment has no limit, so x goes below 0."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rebuild.py',
     'from .lumps import NO_TERMS, Terms, forgiven, lump_terms, motion, moving_lumps\n',
     'from .lumps import NO_TERMS, Terms, drainers, forgiven, lump_terms, motion, moving_lumps\n'),
    ('ashfall_app/engine/rebuild.py',
     '    limit = _limit(v, slope, cap, [h.level for h in holds if h.store == d.id])\n',
     '    limit = None if slope < 0 and drainers(rules, d.id) else _limit(v, slope, cap, [h.level for h in holds if h.store == d.id])\n'),
]
