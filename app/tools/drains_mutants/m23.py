"""Row 23 of MUTANTS_drains.txt: a drain on a tally store accepted by the loader."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/tally_checks.py',
     '{a.store for a in (*c.inputs, *c.drains)} & tallies',
     '{a.store for a in c.inputs} & tallies'),
]
