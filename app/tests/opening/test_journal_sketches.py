"""Every sketch the shipped journal names has a drawing script (docs/research/sketch-test/process.md, "Files"): a sketch
id is /assets/journal/<id>.png, and that file is rendered from `entry_<id>.py` or `note_<id>.py`. A page or note with
no sketch needs none."""
from collections.abc import Iterable
from pathlib import Path

from ashfall_app.opening.schema import Opening
from ashfall_app.opening.subject_checks import slots_of

SKETCH_SCRIPTS = Path(__file__).resolve().parents[3] / "docs" / "research" / "sketch-test"


def sketch_ids(o: Opening) -> list[tuple[str, str | None]]:
    """(where, sketch) for every entry, note and subject slot, a missing sketch as None."""
    named: list[tuple[str, str | None]] = [(f"entry {e.id}", e.sketch) for e in o.entries]
    named += [(f"note {n.id}", n.sketch) for n in o.notes]
    named += [(f"subject {s.id} {k}", slot.sketch) for s in o.subjects for k, slot in slots_of(s)]
    return named


def undrawn(named: Iterable[tuple[str, str | None]], scripts: Path) -> list[str]:
    return [f"{where}: sketch {sketch!r} has no entry_{sketch}.py or note_{sketch}.py" for where, sketch in named
            if sketch is not None and not any((scripts / f"{kind}_{sketch}.py").is_file() for kind in ("entry", "note"))]


def test_every_shipped_sketch_has_a_drawing_script(shipped_opening: Opening):
    named = sketch_ids(shipped_opening)
    assert [s for _, s in named if s is not None], "the shipped journal names no sketch: the check scanned nothing"
    assert undrawn(named, SKETCH_SCRIPTS) == []


def test_an_unknown_sketch_fails_and_a_page_without_one_passes():
    named = [("entry e_wolf", "wolf"), ("note n_knot", "gutter_knot"), ("entry e_place", None),
             ("entry e_planted", "no_such_sketch")]
    assert undrawn(named, SKETCH_SCRIPTS) == [
        "entry e_planted: sketch 'no_such_sketch' has no entry_no_such_sketch.py or note_no_such_sketch.py"]
