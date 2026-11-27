"""Row 04 of MUTANTS_share.txt: band past empty."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/sharelevels.py',
     '    return AtLeast(cond.subject, value, min(release, value, max(value - Q, Q)))\n',
     '    return AtLeast(cond.subject, value, min(release, value, value - Q))\n'),
]
