"""Row 09 of MUTANTS_heldspeed.txt: a standing action's side entry is never held."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/heldentries.py',
     '    return tuple(HeldView(r.id, shares[r.id], tuple(_entry(r.id, w, shares[r.id]) for w in r.while_running))',
     '    return tuple(HeldView(r.id, shares[r.id], tuple(_entry(r.id, w, shares[r.id]) for w in r.while_running\n                                                    if isinstance(r, CardDef) or isinstance(w, HeldSpeed)))'),
]
