"""Row 06 of MUTANTS_spent.txt: each gain rounds up, so a lane's effective shares can sum past its saved ones."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/spent.py", "(g := s_k * share // total) > 0", "(g := -(-s_k * share // total)) > 0"),
]
