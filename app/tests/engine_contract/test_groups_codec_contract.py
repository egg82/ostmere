"""Invariant 182 (engine DESIGN.txt, "GROUPS (pooled lanes)", "Codec", "Rebase"): what a game with no group encodes, and
what a game with one round-trips. The committed saves' hashes, the rules digest and the golden saves are the other half
of the invariant's proof and are other suites'."""
from dataclasses import replace

from ashfall_app.engine import (
    LaneDef, Rules, Save, advance, decode, encode, rebase, rules_digest,
)
from tests.kills import kills
from groups_world import G, GA, P1, P2, cards, join, lane_state, mark, own, split_mix, start, world

KEYS = ("pooled", "group", "own_split", "marks")


def _text(rules: Rules, save: Save) -> str:
    return encode(save, rules)


@kills(9)
def test_182_rules_and_saves_with_no_group_encode_without_any_group_field():
    rules = world((join(P1, own(P1, "a"), True),), lanes=(LaneDef(P1, True),), cards=tuple(c for c in cards() if c.lane == P1))
    save = advance(start(rules), rules, 100)
    text = _text(rules, save)
    for key in KEYS:
        assert f'"{key}"' not in text
    assert lane_state(save, P1).own_split


def test_182_an_unmarked_lane_encodes_its_mark_and_the_group_fields_move_the_digest():
    rules = world((join(P1, GA, False),))
    assert '"own_split"' in _text(rules, start(rules))
    marked = world((join(P1, GA, False), mark(P1, True, own(P1, "a"), at=5)))
    assert rules_digest(marked) != rules_digest(rules)
    assert rules_digest(replace(rules, lanes=(LaneDef(G, True), *rules.lanes[1:]))) != rules_digest(rules)
    assert rules_digest(replace(rules, lanes=tuple(replace(ld, group=None) for ld in rules.lanes))) != rules_digest(rules)


def test_182_a_group_game_round_trips():
    rules = world((join(P1, GA, False), join(P2, own(P2, "a"), True), mark(P2, False, at=5), mark(P2, True, own(P2, "a"), at=9)))
    for t in (0, 5, 100):
        save = advance(start(rules, split_mix((GA, 7000))), rules, t)
        assert decode(_text(rules, save), rules) == save


def test_182_a_save_whose_text_has_no_own_split_decodes_with_every_mark_true():
    rules = world((join(P1, own(P1, "a"), True), join(P2, own(P2, "a"), True)))
    save = advance(start(rules), rules, 50)
    assert "own_split" not in _text(rules, save)
    assert all(lane_state(decode(_text(rules, save), rules), p).own_split for p in (P1, P2))


def test_182_a_save_rebased_under_rules_that_gain_a_group_keeps_its_marks_true_and_runs_on():
    old = world((join(P1, own(P1, "a"), True),), lanes=(LaneDef(P1, True), LaneDef(P2, True)),
                cards=tuple(c for c in cards() if c.lane in (P1, P2)))
    save = advance(start(old), old, 50)
    new = world((join(P1, own(P1, "a"), True),))
    rebased = rebase(_text(old, save), new)
    assert lane_state(rebased, P1).own_split
    assert rebased.mixes == save.mixes and rebased.time == save.time


def test_182_a_trigger_already_true_at_the_rebase_instant_lands_its_mark():
    base = (join(P1, GA, False), join(P2, GA, False))
    old = world(base)
    save = advance(start(old), old, 50)
    new = world((*base, mark(P1, True, own(P1, "a"), at=10)))
    rebased = rebase(_text(old, save), new)
    assert lane_state(rebased, P1).own_split and not lane_state(rebased, P2).own_split
