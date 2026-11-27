"""Row 19 of MUTANTS_leaves.txt, m19c: validation: a Leave in a card's outcome is accepted."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/planchecks.py',
     '        if not once_only:\n            raise InvalidRulesError(f"{where}: only a trigger\'s or an answer\'s outcome has a person leave',
     '        if False:\n            raise InvalidRulesError(f"{where}: only a trigger\'s or an answer\'s outcome has a person leave'),
]
