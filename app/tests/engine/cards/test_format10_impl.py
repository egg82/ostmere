"""FORMAT 10: a chip's off lines take turns (engine design/core.txt, "Chips"). Save.chips_seen counts, 0 before the chip
first shows and then 1 plus the off lines it has said; each hide says the next draw of a shuffle bag over off_lines,
each line once a round and none twice in a row. UPGRADES[9] turns the flags into counts. The bag is the page's own
draw (client/src/game/ledger/fights.ts, bagged): client/fixtures/bag_cases.json holds draws taken from it."""
import json
from pathlib import Path

import pytest

from ashfall_app.engine import (
    UPGRADES, Amount, AtMost, CardDef, CardId, ChipDef, ChipId, Flow, LineKey, Outcome, Rules, Save, StandingDef,
    StateFormatError, StoreDef, StoreId, StoreValue, ActionId, advance_logged, encode, new_save, rebase, view,
)
from ashfall_app.engine.cards.rotation import bagged
from tests.cards_contract.cards_world import Q, rules, tap
from tests.format8 import as_format_9

E, R, TIRED, DRAIN = StoreId("e"), CardId("rest"), ChipId("tired"), ActionId("drain")
OFF = tuple(LineKey(f"tired.off{i}") for i in range(6))
CASES = Path(__file__).resolve().parents[3] / "client" / "fixtures" / "bag_cases.json"


def world(off: tuple[LineKey, ...] = OFF) -> Rules:
    """e drains one a second from ten; tired shows at three or less and clears at six or more; a rest puts seven back."""
    return rules([StoreDef(E, 10 * Q, 10 * Q)], standing=[StandingDef(DRAIN, costs=(Flow(E, Q),))],
                 cards=[CardDef(R, 1, outcome=Outcome(stores=(Amount(E, 7 * Q),)))],
                 chips=[ChipDef(TIRED, AtMost(StoreValue(E), 3 * Q, 6 * Q), off_lines=off)])


def hides(r: Rules, n: int, s: Save) -> tuple[list[str], Save]:
    """The off lines of n show-and-clear rounds from s: run until tired shows, then rest until it clears."""
    keys, t = list[str](), s.time
    for _ in range(n):
        for want in (True, False):
            while (TIRED in view(s, r).chips) != want:
                t += 1
                step = advance_logged(s, r, t)
                s, keys = step.save, keys + [ln.key for ln in step.lines]
            if want:
                s = tap(s, r, t, R)
    return keys, s


def test_the_port_draws_what_the_page_draws():
    cases = json.loads(CASES.read_text())["cases"]
    assert len(cases) >= 9 and all(len(c["draws"]) >= 3 * len(c["pool"]) for c in cases)
    for c in cases:
        assert [bagged(c["key"], c["pool"], k) for k in range(len(c["draws"]))] == c["draws"], c["key"]


@pytest.mark.parametrize("n", [3, 6, 7])
def test_a_bag_spends_each_round_and_never_says_one_line_twice_in_a_row(n: int):
    pool = [f"l{i}" for i in range(n)]
    for key in ("hurt|off", "a|b", "pack|won"):
        drawn = [bagged(key, pool, k) for k in range(60 * n)]
        assert all(sorted(drawn[i:i + n]) == pool for i in range(0, len(drawn), n))
        assert all(a != b for a, b in zip(drawn, drawn[1:]))


def test_a_pool_of_two_takes_turns_from_a_seeded_first():
    firsts = {bagged(key, ["x", "y"], 0) for key in ("a", "b", "c", "d", "e", "f")}
    for key in ("a", "b", "c"):
        drawn = [bagged(key, ["x", "y"], k) for k in range(6)]
        assert drawn[:2] in (["x", "y"], ["y", "x"]) and drawn == drawn[:2] * 3
    assert firsts == {"x", "y"}


def test_each_hide_says_the_next_off_line_and_counts_it():
    r = world()
    keys, s = hides(r, 13, new_save(r))
    assert keys == [bagged("tired|off", OFF, k) for k in range(13)]
    assert s.chips_seen == (14,)
    assert all(a != b for a, b in zip(keys, keys[1:])) and set(keys[:6]) == set(OFF)


def test_a_chip_with_no_off_lines_says_nothing_and_counts_only_its_showing():
    r = world(off=())
    keys, s = hides(r, 3, new_save(r))
    assert keys == [] and s.chips_seen == (1,)


def test_the_turns_carry_across_an_encode_and_a_rebase():
    r = world()
    _, s = hides(r, 4, new_save(r))
    later, _ = hides(r, 3, rebase(encode(s, r), r))
    assert later == [bagged("tired|off", OFF, k) for k in (4, 5, 6)]


def test_upgrade_9_turns_each_flag_into_a_count_and_nothing_else():
    r = world()
    _, s = hides(r, 2, new_save(r))
    old = json.loads(as_format_9(encode(s, r)))
    assert old["save"]["chips_seen"] == [True]
    assert UPGRADES[9](old) == {**old, "format": 10, "save": {**old["save"], "chips_seen": [1]}}
    assert rebase(json.dumps(old, sort_keys=True, separators=(",", ":")), r).chips_seen == (1,)


def test_upgrade_9_refuses_counts():
    r = world()
    doc = json.loads(encode(new_save(r), r))
    with pytest.raises(StateFormatError):
        UPGRADES[9]({**doc, "format": 9, "save": {**doc["save"], "chips_seen": [1]}})
