"""Row 16 of MUTANTS_held.txt: a HANDS fight tap re-reads its odds while it runs (no kept entries)."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/odds.py',
     '        if ls.card == CardId(runner) and ls.speed is not None:\n            return tuple(m for m in ls.speed if is_odds(m) and m.source == odds_source(runner))',
     '        if ls.card == CardId(runner) and ls.speed is not None:\n            return ()'),
]
