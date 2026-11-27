"""Row 04 of MUTANTS_spent.txt: the spent set is kept from its first reading, so a maker brought into play (or a store
that stops being spent) leaves the yield where it was."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/spent.py", "    return _SPENT.get(save, rules, lambda: _spent(save, rules))\n",
     "    return derived(rules, \"_spent_once\", lambda _: _spent(save, rules))\n"),
]
