"""Row 27 of MUTANTS_guards.txt: or-else limits: `or_else` on a rule answering an offer is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/checks.py',
     '''    require(not isinstance(actions[0], (AnswerOffer, AnswerKind)),''',
     '''    require(True or not isinstance(actions[0], (AnswerOffer, AnswerKind)),'''),
]
