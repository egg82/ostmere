"""Row 23 of MUTANTS.txt: reach at tap start."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chains.py',
     'from .work import apply_outcome\n',
     'from .work import apply_outcome\n\n_MEMO: dict[tuple[int, str], StrengthExplanation] = {}\n'),
    ('ashfall_app/engine/chains.py',
     '    return explain_over(base_stack(save, rules), rules, ChainReach(card))\n',
     '    return _MEMO.setdefault((id(rules), card), explain_over(base_stack(save, rules), rules, ChainReach(card)))\n'),
]
