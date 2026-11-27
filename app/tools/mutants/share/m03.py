"""Row 03 of MUTANTS_share.txt: band past full."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/sharelevels.py',
     '        return AtMost(cond.subject, value, max(release, value, min(value + Q, whole * Q - 1)))\n',
     '        return AtMost(cond.subject, value, max(release, value, value + Q))\n'),
]
