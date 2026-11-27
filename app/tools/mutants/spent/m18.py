"""Row 18 of MUTANTS_spent.txt: the hands mix's yield is kept while the running cards' kinds stay the same, so a SaveMix edit leaves the old gains."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/mixruns.py',
     'def _mix_entries(save: Save, rules: Rules) -> tuple[Entries, Gains]:\n',
     '_STALE = {}\n\n\ndef _mix_entries(save: Save, rules: Rules) -> tuple[Entries, Gains]:\n'),
    ('ashfall_app/engine/mixruns.py',
     '    return yielded(entries, lambda _: HANDS)\n',
     '    return _STALE.setdefault((id(rules), mix.id, tuple((c, r.kind) for c, _, r in entries)),\n                             yielded(entries, lambda _: HANDS))\n'),
]
