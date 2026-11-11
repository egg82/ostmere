"""A retune across a release (engine DESIGN.txt, "Rebase" step 5, invariant 51) keeps a card's bar at its fraction,
tapped or mixed, so the lump its work pays still totals exactly one completion's amount and a beat waiting on that
amount fires. The shape of a format 7 save mid-walk while tired, whose walk's work_s doubles in the new rules."""
import json

from ashfall_app.engine import (
    BP, HANDS, Amount, AtLeast, AtMost, CardDef, CardId, ChipDef, ChipId, Flow, LaneSpeed, LineKey, Outcome, Rules,
    Save, StandingDef, StoreDef, StoreId, StoreValue, ActionId, TriggerDef, TriggerId, advance, advance_logged, encode,
    new_save, rebase,
)
from tests.cards_contract.cards_world import Q, lane, mul, rules, tap, val, with_mix

E, BACK = StoreId("e"), StoreId("back")
WALK, MIXED = CardId("walk"), CardId("mixed")
DRAIN = ActionId("drain")


def world(walk_s: int, mixed_s: int = 100) -> Rules:
    """e starts at 2 items, so tired (at most 3) shows from the start and stays: nothing refills it. The walk pays
    one item of `back`, and a trigger waits on that whole item."""
    tired = ChipDef(ChipId("tired"), AtMost(StoreValue(E), 3 * Q, 6 * Q), (mul(LaneSpeed(HANDS), 5000, "tired"),),
                    None, None)
    came_back = TriggerDef(TriggerId("came_back"), AtLeast(StoreValue(BACK), Q, Q),
                           Outcome(lines=(LineKey("came_back"),)))
    return rules([StoreDef(E, 10 * Q, 2 * Q), StoreDef(BACK, Q, 0)],
                 standing=[StandingDef(DRAIN, costs=(Flow(E, 1),))],
                 cards=[CardDef(WALK, walk_s, cap=1, outcome=Outcome(stores=(Amount(BACK, Q),)),
                                lines=(LineKey("walk.done"),)), CardDef(MIXED, mixed_s)],
                 chips=[tired], triggers=[came_back])


def as_format_7(text: str) -> str:
    doc = json.loads(text)
    for ls in doc["save"]["lanes"]:
        del ls["speed"]
    return json.dumps({**doc, "format": 7}, sort_keys=True, separators=(",", ":"))


def work_of(s: Save, card: CardId) -> int:
    return next(cs.work.start_value for cs in s.cards if cs.card == card)


def test_a_tap_retuned_mid_walk_pays_its_whole_lump_and_the_beat_on_it_fires():
    old, new = world(7200), world(14_400)
    s = advance(tap(new_save(old), old, 0, WALK), old, 3823)   # about a quarter of its work done at half speed
    assert 0 < work_of(s, WALK) < 7200 * BP
    moved = rebase(as_format_7(encode(s, old)), new)
    assert lane(moved, HANDS).card == WALK
    keys = [ln.key for ln in advance_logged(moved, new, moved.time + 100_000).lines]
    after = advance(moved, new, moved.time + 100_000)
    assert val(after, new, BACK) == Q
    assert "walk.done" in keys and "came_back" in keys


def test_a_retuned_card_keeps_its_bar_fraction_tapped_or_mixed():
    old = world(7200, mixed_s=100)
    s = advance(with_mix(new_save(old), old, 0, {MIXED: BP}), old, 50)
    s = advance(tap(s, old, 50, WALK), old, 1000)
    mixed_before, walk_before = work_of(s, MIXED), work_of(s, WALK)
    assert 0 < mixed_before < 100 * BP and 0 < walk_before < 7200 * BP
    longer = rebase(encode(s, old), world(14_400, mixed_s=200))
    assert work_of(longer, MIXED) == mixed_before * 2
    assert work_of(longer, WALK) == walk_before * 2
    assert lane(longer, HANDS).card == WALK
