"""Retiring a journal note or page (renames.toml): a retired note retires the trigger the loader made for it too, which
the engine's rebase then lets a save drop (engine.Retired)."""
from ashfall_app.engine import Retired, TriggerId
from ashfall_app.opening.renames import RenameEntry, engine_renames, with_made


def retire(kind: str, old: str) -> RenameEntry:
    return RenameEntry.model_validate({"kind": kind, "from": old})


def test_the_engine_is_told_of_a_retired_notes_trigger_and_of_nothing_else():
    got = engine_renames(with_made([retire("note", "n_x"), retire("entry", "e_x"), retire("line", "l_x")]))
    assert got == (Retired(TriggerId("note_n_x")),)
