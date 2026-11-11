"""The journal on the wire (api/CONTRACT.txt, "JOURNAL", acceptance 5): Content.journal null without [journal] and served
in content order with hands resolved otherwise, its components in the spec, and journal_read kept on the account."""
from dataclasses import replace
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from ashfall_app.api import content_models as cm
from ashfall_app.api.service import Game
from ashfall_app.main import create_app
from ashfall_app.opening.schema import load_opening
from tests.opening.bookless import bookless_opening
from ashfall_app.saves.ruleset import ruleset
from tests.game_client import GameClient

FIXTURE = Path(__file__).resolve().parent / "opening" / "fixtures" / "journal.toml"


def game_of(*chapters: Path) -> Game:
    o = load_opening(bookless_opening(), chapters)
    return Game(o, replace(ruleset(o, [], "test", 1)))


@cache
def journal_game() -> Game:
    return game_of(FIXTURE)


def test_content_has_no_journal_without_a_book():
    assert game_of().content().journal is None


def test_content_serves_the_book_its_pages_and_notes_in_content_order_with_hands_resolved():
    assert journal_game().content().journal == cm.JournalInfo(feature="book", entries=[
        cm.EntryInfo(entry="j_page_a", section=cm.Section.CREATURES, sketch="j_sketch_a", runners=["t_hunt", "t_raid"], notes=[
            cm.NoteInfo(note="j_note_a1", hand=cm.Hand.INK, sketch=None),
            cm.NoteInfo(note="j_note_a2", hand=cm.Hand.PENCIL, sketch="j_note_sketch")]),
        cm.EntryInfo(entry="j_page_b", section=cm.Section.PLACES, sketch="j_sketch_b", runners=[], notes=[
            cm.NoteInfo(note="j_note_b1", hand=cm.Hand.PENCIL, sketch=None)])])


def test_a_notes_words_are_its_text_entry():
    text = {t.key: t.text for t in journal_game().content().text_entries}
    assert all(n.note in text for e in (journal_game().content().journal or cm.JournalInfo(feature="", entries=[])).entries
               for n in e.notes) and "j_note_a1" in text


def test_the_spec_names_the_journals_components():
    schemas: dict[str, Any] = create_app().openapi()["components"]["schemas"]
    assert {"JournalInfo", "EntryInfo", "NoteInfo", "Hand", "Section"} <= set(schemas)
    assert schemas["Hand"]["enum"] == ["ink", "pencil"]
    assert schemas["Section"]["enum"] == ["days", "creatures", "places"]
    assert schemas["EntryInfo"]["properties"]["sketch"]["anyOf"] == [{"type": "string"}, {"type": "null"}]
    assert schemas["Content"]["properties"]["journal"]["anyOf"][0] == {"$ref": "#/components/schemas/JournalInfo"}


def test_journal_read_is_empty_on_a_new_account_and_round_trips(game: GameClient):
    game.begin()
    assert game.client.get("/api/me").json()["account"]["presentation"]["journal_read"] == []
    r = game.client.put("/api/me/presentation", json={"journal_read": ["a", "b"]})
    assert r.status_code == 200 and r.json()["presentation"]["journal_read"] == ["a", "b"]
    assert game.client.get("/api/me").json()["account"]["presentation"]["journal_read"] == ["a", "b"]


@pytest.mark.parametrize("body", [{"journal_read": ["a"] * 513}, {"journal_read": ["x" * 65]}])
def test_journal_read_past_the_limits_is_refused(game: GameClient, body: dict[str, Any]):
    game.begin()
    assert game.client.put("/api/me/presentation", json=body).status_code == 422
