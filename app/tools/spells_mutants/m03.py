"""Row 03 of MUTANTS.txt: due ignores links."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     '    done = _whole(save, rules, fight.fought) + (0 if fight.chained is None else _whole(save, rules, fight.chained))\n',
     '    done = _whole(save, rules, fight.fought)\n'),
]
