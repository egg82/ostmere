"""Row 02 of MUTANTS_heldspeed.txt: standing holders are never held."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '                                                 *(a for a in r.standing if a.while_running)))',
     '                                                 ))'),
]
