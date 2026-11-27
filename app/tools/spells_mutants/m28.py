"""Row 28 of MUTANTS.txt: fight card chains."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/chaincheck.py',
     '_require(c.fight is None, f"{where}: a fight card',
     '_require(True, f"{where}: a fight card'),
]
