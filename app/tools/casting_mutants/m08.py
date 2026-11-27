"""Row 08 of MUTANTS.txt: non person."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/casts.py',
     '    return [x.id for x in o.lanes if x.ruled and not x.pooled and not x.station and x.name_key is not None]\n',
     '    return [x.id for x in o.lanes if x.ruled]\n'),
]
