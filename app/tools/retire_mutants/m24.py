"""Row 24 of MUTANTS_leaves.txt, m24: logs nothing: a season's removed orders are logged with ended None."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rulelog.py',
     '        why = Ended.SEASON if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else None\n',
     '        why = None if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else None\n'),
]
