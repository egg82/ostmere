"""A served line says whether it opens a story beat (api/CONTRACT.txt, "Beat lines"): the content's `[beat_lines]`
decide, never a key's name, and a beat's id is one of content/beats.yaml's."""
import re
from dataclasses import replace
from pathlib import Path

from ashfall_app.api.service import Game
from ashfall_app.engine import Line, LineKey
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.ruleset import ruleset

BEATS = Path(__file__).resolve().parents[2] / "content" / "beats.yaml"


def game() -> tuple[Game, dict[str, list[str]]]:
    o = load_opening()
    return Game(o, replace(ruleset(o, "test", 1))), o.beat_lines


def served(g: Game, key: str) -> bool:
    return g.log_line(Line(time=1, seq=0, key=LineKey(key), card=None)).opens_beat


def test_a_beats_first_line_opens_it_and_its_other_lines_do_not():
    g, beats = game()
    openers = [k for keys in beats.values() for k in keys]
    assert openers and all(served(g, k) for k in openers)   # control: the field is set where authored
    assert not served(g, "l_b3_2")   # the same beat's later line
    assert not served(g, "l_look_out_2")   # a card's closing line
    assert not served(g, "l_dusk_1")   # the end's lines are the page's (Content.end_line_keys)


def test_a_beat_with_two_ways_to_be_told_opens_on_either():
    g, beats = game()
    assert len(beats["B4"]) == 2 and all(served(g, k) for k in beats["B4"])


def test_the_field_follows_the_content_not_the_key():
    o = load_opening()
    g = Game(o, replace(ruleset(o, "test", 1)))
    assert served(g, "l_b3_1") and not served(g, "l_b3_1_but_not_authored")


def test_every_beat_id_is_a_beat_of_the_schedule():
    ids = set(re.findall(r"\{id: ([A-Z]\d+),", BEATS.read_text()))
    _, beats = game()
    assert beats and ids and set(beats) <= ids   # control: the schedule parsed
