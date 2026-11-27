"""A served line says whether it opens a story beat (api/contract/endpoints.txt, "Beat lines"): the content's `[beat_lines]`
decide, never a key's name, and a beat's id is one of content/beats.yaml's."""
import re
from pathlib import Path

import pytest

from ashfall_app.api.service import Game
from ashfall_app.engine import Line, LineKey
from ashfall_app.rules.schema import Opening
from tests.shipped_ruleset import ShippedRuleset

BEATS = Path(__file__).resolve().parent.parents[2] / "content" / "beats.yaml"


@pytest.fixture(scope="module")
def game(shipped_opening: Opening, shipped_ruleset: ShippedRuleset) -> Game:
    return shipped_ruleset.make_game(shipped_opening, shipped_ruleset.rs)


def served(g: Game, key: str) -> bool:
    return g.log_line(Line(time=1, seq=0, key=LineKey(key), card=None)).opens_beat


def test_a_beats_first_line_opens_it_and_its_other_lines_do_not(game: Game, shipped_opening: Opening):
    g, beats = game, shipped_opening.beat_lines
    openers = [k for keys in beats.values() for k in keys]
    assert openers and all(served(g, k) for k in openers)   # control: the field is set where authored
    assert not served(g, "l_b3_2")   # the same beat's later line
    assert not served(g, "l_look_out_2")   # a card's closing line
    assert not served(g, "l_dusk_1")   # the end's lines are the page's (Content.end_line_keys)


def test_a_beat_with_two_ways_to_be_told_opens_on_either(game: Game, shipped_opening: Opening):
    beats = shipped_opening.beat_lines
    assert len(beats["B4"]) == 2 and all(served(game, k) for k in beats["B4"])


def test_the_field_follows_the_content_not_the_key(game: Game):
    assert served(game, "l_b3_1") and not served(game, "l_b3_1_but_not_authored")


def test_every_beat_id_is_a_beat_of_the_schedule(shipped_opening: Opening):
    ids = set(re.findall(r"\{id: ([A-Z]\d+),", BEATS.read_text()))
    beats = shipped_opening.beat_lines
    assert beats and ids and set(beats) <= ids   # control: the schedule parsed
