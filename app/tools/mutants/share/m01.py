"""Row 01 of MUTANTS_share.txt: nearest item."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/sharelevels.py',
     '    items = b * whole // BP + 1 if floor_side else ceil_div(b * whole, BP)\n',
     '    items = (2 * b * whole + BP) // (2 * BP) + (1 if floor_side else 0)\n'),
]
