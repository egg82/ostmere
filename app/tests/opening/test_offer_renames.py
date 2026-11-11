"""An offer's rename carries its trigger's (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Release
lock", "Content"). The loader makes one trigger per offer, id "offer_" + the offer's id, so a rename of an offer in
renames.toml names the offer only: the loader derives "offer_" + old to "offer_" + new, adds it to the renames it
passes (what rebase gets), and the lock records both as applied. Read through the same calls the server and
tools/content_lock.py make: load_renames, then engine_renames and lock.snapshot."""
from pathlib import Path

import pytest

from ashfall_app.engine import IdKind, Rename
from ashfall_app.opening.lock import snapshot
from ashfall_app.opening.renames import engine_renames, load_renames
from tests.opening.playthrough import opening, opening_rules


@pytest.fixture(scope="module", autouse=True)
def built() -> None:
    """The cached opening and its rules, built in setup so no test's timed call pays for them."""
    opening_rules()


def renames_file(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "renames.toml"
    path.write_text(body)
    return path


def test_an_offer_rename_carries_its_triggers_rename_to_rebase_and_to_the_lock(tmp_path: Path):
    path = renames_file(tmp_path, '[[renames]]\nkind = "offer"\nfrom = "ask"\nto = "ask2"\n')
    entries = load_renames(path)
    passed = set(engine_renames(entries))
    assert Rename(IdKind.OFFER, "ask", "ask2") in passed
    assert Rename(IdKind.TRIGGER, "offer_ask", "offer_ask2") in passed
    recorded = {(r["kind"], r["from"], r["to"]) for r in snapshot(opening(), opening_rules(), entries).renames}
    assert {("offer", "ask", "ask2"), ("trigger", "offer_ask", "offer_ask2")} <= recorded


def test_an_answer_rename_carries_nothing_else(tmp_path: Path):
    """Only an offer has a trigger of its own: an answer's rename is passed as it is, alone (the control)."""
    path = renames_file(tmp_path, '[[renames]]\nkind = "answer"\nfrom = "yes"\nto = "aye"\n')
    assert set(engine_renames(load_renames(path))) == {Rename(IdKind.ANSWER, "yes", "aye")}
