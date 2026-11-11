"""FORMAT 8: a hands tap keeps its start speed on its LaneState (engine DESIGN.txt, "Speed"), and UPGRADES[7] adds
speed None to every lane, so a tap a format 7 save began reads the live stack to its end, as it did then."""
import json

import pytest

from ashfall_app.engine import (
    FORMAT, HANDS, UPGRADES, AfterTime, CardDef, CardId, ChipDef, ChipId, LaneSpeed, LineKey, StateFormatError,
    advance_logged, encode, new_save, rebase,
)
from tests.cards_contract.cards_world import lane, mul, rules, tap

CD = CardId("cd")


def world():
    slow = mul(LaneSpeed(HANDS), 5000, "tired")
    return rules([], cards=[CardDef(CD, 100, lines=(LineKey("cd.tap"),))],
                 chips=[ChipDef(ChipId("tired"), AfterTime(50), (slow,), None, None)])


def as_format_7(text: str) -> str:
    doc = json.loads(text)
    for ls in doc["save"]["lanes"]:
        del ls["speed"]
    return json.dumps({**doc, "format": 7}, sort_keys=True, separators=(",", ":"))


def test_a_hands_tap_keeps_its_start_speed_and_a_format_7_tap_reads_the_live_stack():
    r = world()
    s = tap(new_save(r), r, 0, CD)
    assert FORMAT >= 8 and lane(s, HANDS).speed == ()
    old = rebase(as_format_7(encode(s, r)), r)
    assert lane(old, HANDS).speed is None and lane(old, HANDS).card == CD
    landed = [ln.time for ln in advance_logged(old, r, 400).lines if ln.key == "cd.tap"]
    assert landed == [150]   # half its work at full speed, half at the chip's half
    assert [ln.time for ln in advance_logged(s, r, 400).lines if ln.key == "cd.tap"] == [100]


def test_upgrade_7_adds_speed_none_to_each_lane_and_nothing_else():
    r = world()
    text = encode(tap(new_save(r), r, 0, CD), r)
    old = json.loads(as_format_7(text))
    up = UPGRADES[7](old)
    lanes = [{**ls, "speed": None} for ls in old["save"]["lanes"]]
    assert up == {**old, "format": 8, "save": {**old["save"], "lanes": lanes}}


def test_upgrade_7_refuses_a_lane_that_already_keeps_a_speed():
    r = world()
    doc = json.loads(encode(new_save(r), r))
    with pytest.raises(StateFormatError):
        UPGRADES[7]({**doc, "format": 7})
