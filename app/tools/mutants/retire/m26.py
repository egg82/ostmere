"""Row 26 of MUTANTS_leaves.txt, m26: cancels the tap: the turn frees the lanes running a named card."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     'def _free(save: Save, lane: LaneId) -> Save:\n',
     'def _free_named(save: Save, cards: tuple[CardId, ...]) -> Save:\n    for ls in save.lanes:\n        if ls.card in cards:\n            save = _free(save, ls.lane)\n    return save\n\n\ndef _free(save: Save, lane: LaneId) -> Save:\n'),
    ('ashfall_app/engine/work.py',
     '    save = rebuild(_end_retired_taps(queued(save, rules, o.queues), rules), rules)\n',
     '    save = rebuild(_free_named(_end_retired_taps(queued(save, rules, o.queues), rules), o.retire_orders), rules)\n'),
]
