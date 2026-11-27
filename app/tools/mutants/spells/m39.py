"""Row 39 of MUTANTS.txt: chains not served."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/convert.py',
     'chains=[w.Chain(card=c.card, runner=c.runner, up_to=_strength(c.reach, {})) for c in chains])',
     'chains=[])'),
]
