"""Row 01 of MUTANTS_or_else.txt: `actions` is just `then`: or_else is stored but never read back."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders.py',
     '        return (self.then, *self.or_else)\n',
     '        return (self.then,)\n'),
]
