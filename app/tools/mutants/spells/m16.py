"""Row 16 of MUTANTS.txt: stale second chain."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/combat/chains.py',
     'from ..loop.work import apply_outcome\n',
     'from ..loop.work import apply_outcome\n\n_MEMO: dict[tuple[int, int, str], int] = {}\n'),
    ('ashfall_app/engine/combat/chains.py',
     '    return members - done % members\n',
     '    done = _MEMO.setdefault((id(rules), save.time, runner), done)\n    return members - done % members\n'),
]
