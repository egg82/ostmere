"""Row 24 of MUTANTS_leaves.txt, m24b: logs nothing: a season's removed orders are logged ended LEFT."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rulelog.py',
     '        why = Ended.SEASON if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else None\n',
     '        why = Ended.LEFT if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else None\n'),
]
