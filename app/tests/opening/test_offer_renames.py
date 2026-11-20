"""An offer's rename carries its trigger's (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Release
lock", "Content"). The loader makes one trigger per offer, id "offer_" + the offer's id, so a rename of an offer in
renames.toml names the offer only: the loader derives "offer_" + old to "offer_" + new, adds it to the renames it
passes (what rebase gets). Read through the same calls the server makes: load_renames, then engine_renames."""
from pathlib import Path

from ashfall_app.engine import IdKind, Rename
from ashfall_app.opening.renames import engine_renames, load_renames


def renames_file(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "renames.toml"
    path.write_text(body)
    return path


def test_an_offer_rename_carries_its_triggers_rename_to_rebase(tmp_path: Path):
    path = renames_file(tmp_path, '[[renames]]\nkind = "offer"\nfrom = "ask"\nto = "ask2"\n')
    entries = load_renames(path)
    passed = set(engine_renames(entries))
    assert Rename(IdKind.OFFER, "ask", "ask2") in passed
    assert Rename(IdKind.TRIGGER, "offer_ask", "offer_ask2") in passed


def test_an_answer_rename_carries_nothing_else(tmp_path: Path):
    """Only an offer has a trigger of its own: an answer's rename is passed as it is, alone (the control)."""
    path = renames_file(tmp_path, '[[renames]]\nkind = "answer"\nfrom = "yes"\nto = "aye"\n')
    assert set(engine_renames(load_renames(path))) == {Rename(IdKind.ANSWER, "yes", "aye")}
