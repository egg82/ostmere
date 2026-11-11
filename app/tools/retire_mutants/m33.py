"""Row 33 of MUTANTS_leaves.txt, m33: ended too often: any removed tap order is logged ended, a SetOrders removal included."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/rulelog.py',
     '        why = Ended.SEASON if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else None\n',
     '        why = Ended.SEASON if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else Ended.SEASON\n'),
]
