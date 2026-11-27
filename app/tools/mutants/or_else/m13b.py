"""Row 13 of MUTANTS_or_else.txt: order_doing is None whatever runs."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/plan.py',
     'o.actions.index(doing[i]) if i in doing else None',
     'None'),
]
