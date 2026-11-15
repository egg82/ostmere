"""Row 02 of MUTANTS_share.txt: no band."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/sharelevels.py',
     '        return AtMost(cond.subject, value, max(release, value, min(value + Q, whole * Q - 1)))\n',
     '        return AtMost(cond.subject, value, max(release, value))\n'),
]
