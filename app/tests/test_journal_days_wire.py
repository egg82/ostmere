"""The journal's written days on the wire (api/contract/journal.txt, "JOURNAL", "The written days"): a Step carries the
written days it composed, an Opened every written day stored before it, each note with its slot, text key, resolved
hand and sketch; a day not written is never served; the spec names the shapes; and SavePresentation.newest_day_read
only grows."""
from dataclasses import replace
from typing import Any

import psycopg
import pytest

from ashfall_app.api import journal_models as jm
from ashfall_app.api.service import Game
from ashfall_app.main import create_app
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.journal import DAY_S, ComposedDay, Note
from ashfall_app.saves.journal_rules import Look, journal_rules
from tests.game_client import GameClient
from tests.kills import kills
from tests.saves.journal.journal_fixture import JOURNAL, a_beat_line
from tests.shipped_ruleset import ShippedRuleset


def store_line(url: str, save_id: int, at: int, key: str) -> None:
    with psycopg.connect(url) as c:
        c.execute("INSERT INTO save_lines (save_id, n, at, key) SELECT %s, coalesce(max(n) + 1, 0), %s, %s"
                  " FROM save_lines WHERE save_id = %s", (save_id, at, key, save_id))


def test_the_spec_names_the_days_and_requires_them_on_step_and_opened():
    schemas: dict[str, Any] = create_app().openapi()["components"]["schemas"]
    assert {"JournalDay", "DayNote", "Slot"} <= set(schemas)
    for model in ("Step", "Opened"):
        assert "journal_days" in schemas[model]["required"]
        assert schemas[model]["properties"]["journal_days"]["items"] == {"$ref": "#/components/schemas/JournalDay"}
    assert schemas["DayNote"]["required"] == ["subject", "slot", "key", "hand", "sketch", "count"]
    assert schemas["Slot"]["enum"] == ["first", "repeat", "catchup", "mention", "late", "misremember", "correction",
                                       "loss", "fold"]
    day_read = schemas["SavePresentation"]["properties"]["newest_day_read"]
    assert {"type": "integer", "minimum": 0, "maximum": 2**53 // DAY_S} in day_read["anyOf"]


def test_a_step_carries_the_written_days_it_composed_and_an_open_every_one_stored_before_it(
        game: GameClient, pg_url: str, shipped_opening: Opening):
    key, subject = a_beat_line(shipped_opening)
    j = journal_rules(shipped_opening)
    told = next(s for s in j.subjects if s.id == subject)
    look = j.looks[(subject, "first")]
    save_id = int(game.begin()["save"]["save_id"])
    store_line(pg_url, save_id, DAY_S + 30, key)
    game.clock.tick(3 * DAY_S + 60)
    step = game.advance(save_id)
    assert step.status_code == 200, step.text
    days = step.json()["journal_days"]
    assert [d["day"] for d in days] == [1], "day 1 holds the beat; days 0 and 2 are blank and not served"
    [note] = days[0]["day_notes"]
    assert note["key"] in told.first
    assert note == {"subject": subject, "slot": "first", "key": note["key"], "hand": look.hand, "sketch": look.sketch,
                    "count": None}
    game.clock.tick(DAY_S)
    opened = game.client.post(f"/api/saves/{save_id}/open")
    assert opened.status_code == 200, opened.text
    assert opened.json()["journal_days"] == days and opened.json()["step"]["journal_days"] == []
    again = game.client.post(f"/api/saves/{save_id}/open")
    assert again.json()["journal_days"] == days, "a day once served is served the same"


@kills(12, 13)
def test_each_note_is_in_its_slots_hand_and_sketch_and_one_whose_slot_names_none_in_ink(
        shipped_ruleset: ShippedRuleset):
    looks = {("s_a", "first"): Look("pencil", "j_sketch"), ("s_a", "late"): Look("ink", None)}
    game = Game(shipped_ruleset.opening, replace(shipped_ruleset.rs, journal=replace(JOURNAL, looks=looks)))
    notes = (Note("s_a", "first", "k.1"), Note("s_crowd", "mention", "k.2"), Note("s_a", "late", "k.3"))
    served = game.journal_days((ComposedDay(0, (), "busy"), ComposedDay(1, notes, None, ("soot", "smudge")), ComposedDay(2, (), None)))
    assert served == [jm.JournalDay(day=1, day_notes=[
        jm.DayNote(subject="s_a", slot=jm.Slot.FIRST, key="k.1", hand=jm.Hand.PENCIL, sketch="j_sketch", count=None),
        jm.DayNote(subject="s_crowd", slot=jm.Slot.MENTION, key="k.2", hand=jm.Hand.INK, sketch=None, count=None),
        jm.DayNote(subject="s_a", slot=jm.Slot.LATE, key="k.3", hand=jm.Hand.INK, sketch=None, count=None)], marks=[jm.Mark.SOOT, jm.Mark.SMUDGE])]


def test_a_step_that_writes_no_note_carries_no_day(game: GameClient):
    save_id = int(game.begin()["save"]["save_id"])
    game.clock.tick(3600)
    r = game.advance(save_id)
    assert r.status_code == 200 and r.json()["journal_days"] == []


def put_day(game: GameClient, save_id: int, body: dict[str, Any]) -> Any:
    return game.client.put(f"/api/saves/{save_id}/presentation", json=body)


@kills(14)
def test_newest_day_read_only_grows(game: GameClient):
    save_id = int(game.begin()["save"]["save_id"])
    assert put_day(game, save_id, {}).json()["newest_day_read"] is None
    kept = [put_day(game, save_id, body).json()["newest_day_read"]
            for body in ({"newest_day_read": 5}, {"newest_day_read": 3}, {"newest_day_read": None}, {"lessons": ["l"]},
                         {"newest_day_read": 7})]
    assert kept == [5, 5, 5, 5, 7]


@pytest.mark.parametrize("bad", [-1, 2**53 // DAY_S + 1])
def test_newest_day_read_out_of_bounds_is_refused(game: GameClient, bad: object):
    save_id = int(game.begin()["save"]["save_id"])
    assert put_day(game, save_id, {"newest_day_read": bad}).status_code == 422
