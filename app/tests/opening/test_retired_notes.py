"""Retiring a journal note or page (engine DESIGN.txt, "Release lock"; renames.toml): a `note` or `entry` entry with no
`to` answers the lock for a released id the content dropped; a retired note retires the trigger the loader made for it
too, which the engine's rebase then lets a save drop (engine.Retired), and a retired id back in the content is
forbidden as a renamed-away one is."""
from ashfall_app.engine import Retired, TriggerId
from ashfall_app.opening.renames import RenameEntry, engine_renames, with_made
from tests.opening.test_released import found, released, shipped_built


def retire(kind: str, old: str) -> RenameEntry:
    return RenameEntry.model_validate({"kind": kind, "from": old})


def test_a_retired_note_answers_for_the_note_and_its_trigger():
    lock = released(note=["ghost_note"], trigger=["note_ghost_note"])
    told = found(shipped_built(), lock=lock)
    assert {"note ghost_note was removed", "trigger note_ghost_note was removed"} <= {
        p.message.split(":")[0] for p in told if p.cls == "needs_mapping"}, told   # control: both are told
    assert not any("ghost_note" in p.message for p in found(shipped_built(), with_made([retire("note", "ghost_note")]), lock=lock))


def test_a_retired_entry_answers_for_the_entry():
    lock = released(entry=["ghost_entry"])
    assert any("entry ghost_entry was removed" in p.message for p in found(shipped_built(), lock=lock))
    assert not any("ghost_entry" in p.message for p in found(shipped_built(), [retire("entry", "ghost_entry")], lock=lock))


def test_a_retired_note_back_in_the_content_is_forbidden():
    o, _ = shipped_built()
    live = o.notes[0].id
    ps = found(shipped_built(), [retire("note", live)])
    assert any(p.cls == "forbidden" and f"note {live} was renamed away" in p.message for p in ps), ps


def test_the_engine_is_told_of_a_retired_notes_trigger_and_of_nothing_else():
    got = engine_renames(with_made([retire("note", "n_x"), retire("entry", "e_x"), retire("line", "l_x")]))
    assert got == (Retired(TriggerId("note_n_x")),)
