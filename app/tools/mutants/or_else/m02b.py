"""Row 02 of MUTANTS_or_else.txt: `actions` is reversed, so every reader sees the list last to first."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/orders.py',
     '        return (self.then, *self.or_else)\n',
     '        return (*reversed(self.or_else), self.then)\n'),
]
