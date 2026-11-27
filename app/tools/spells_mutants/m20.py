"""Row 20 of MUTANTS.txt: links out of order."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/handlers.py',
     '    if c.cap is not None:\n        own = written_by(c)\n        save, lines = complete(save, rules, card)\n        for key in lines:\n            emit(save.time, key, card if key in own else None)\n    if c.chain is None:\n        return save, True, 0\n    save, links, shown = resolve(save, rules, card, room)\n    for key in links:\n        emit(save.time, key, card)\n    for key in shown:\n        emit(save.time, key, None)\n    return save, c.cap is not None or bool(links), len(links)\n',
     '    if c.chain is None:\n        links: tuple = ()\n    else:\n        save, links, shown = resolve(save, rules, card, room)\n        for key in links:\n            emit(save.time, key, card)\n        for key in shown:\n            emit(save.time, key, None)\n    if c.cap is not None:\n        own = written_by(c)\n        save, lines = complete(save, rules, card)\n        for key in lines:\n            emit(save.time, key, card if key in own else None)\n    return save, c.cap is not None or bool(links), len(links)\n'),
]
