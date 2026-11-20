"""Groups on the wire (api/CONTRACT.txt, "GROUPS"), on the test chapter tests/opening/fixtures/groups_wire.toml merged
after the shipped content: a pooled lane t_crew, two people handed to it (t_m1, t_m3) and one marked (t_m2). The
content's pooled and group, the view's own_split and crew, each a plain copy of the engine's."""
from functools import cache
from pathlib import Path

import pytest

from ashfall_app import engine as e
from ashfall_app import main
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules
from ashfall_app.saves.ruleset import ruleset

FIXTURE = Path(__file__).resolve().parent / "opening" / "fixtures" / "groups_wire.toml"
CREW_CARD = "t_crew_work"
WORKED = 400   # after the third join (300): two members of the group, one marked person


@pytest.fixture(scope="module", autouse=True)
def _shipped(shipped_opening: Opening):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(main, "load_opening", lambda: shipped_opening)
        yield


@cache
def opening() -> Opening:
    return merge_chapters(main.load_opening(), (FIXTURE,))


def game() -> Game:
    return Game(opening(), ruleset(opening(), "test", 1))


def wire() -> w.View:
    r = to_rules(opening())
    return game().view(e.advance(e.new_save(r), r, WORKED))


def test_the_content_serves_the_pooled_lane_and_each_persons_group():
    lanes = {x.lane: x for x in game().content().lane_infos}
    assert (lanes["t_crew"].pooled, lanes["t_crew"].group, lanes["t_crew"].name_key) == (True, None, None)
    assert [(lanes[p].pooled, lanes[p].group) for p in ("t_m1", "t_m2", "t_m3")] == [(False, "t_crew")] * 3
    assert (lanes["hands"].pooled, lanes["hands"].group) == (False, None)


def test_the_content_serves_the_person_a_group_is_tied_to():
    lanes = {x.lane: x for x in game().content().lane_infos}
    assert lanes["t_crew"].tied == "t_m2"
    assert [lanes[k].tied for k in ("t_m1", "t_m2", "t_m3", "hands")] == [None] * 4


def test_the_view_serves_each_persons_mark():
    marks = {b.lane: b.own_split for b in wire().lanes}
    assert {k: marks[k] for k in ("t_m1", "t_m2", "t_m3")} == {"t_m1": False, "t_m2": True, "t_m3": False}
    assert marks["t_crew"] is None and marks["hands"] is None


def test_the_view_serves_a_group_cards_crew():
    cards = {c.card: c for c in wire().cards}
    assert cards[CREW_CARD].crew == 2 and cards[CREW_CARD].share_bp == 2 * 10_000
    assert all(c.crew is None for k, c in cards.items() if k != CREW_CARD)


def test_a_group_card_is_not_tapped():
    r = to_rules(opening())
    s = e.advance(e.new_save(r), r, WORKED)
    with pytest.raises(e.InvalidVerbError):
        e.decide(s, r, WORKED, game().verb(w.TapCard(card=CREW_CARD)))
