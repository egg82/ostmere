"""Row 20 of MUTANTS_drains.txt: `every` divides value but not release."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/opening/convert.py',
     '    return units(c.value) // c.every, units(release) // c.every\n',
     '    return units(c.value) // c.every, units(release)\n'),
]
