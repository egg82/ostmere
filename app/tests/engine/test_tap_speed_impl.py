"""A tap on the hands runs at the speed it had at its start (DESIGN.txt, "Speed"): a chip that shows or clears during
it, or a speed entry an outcome adds, leaves the tap's lines alone and applies from its end; the mix runs under the
live stack throughout, and the time shown before the tap is the time it takes. The queue's head waits while a chip's
rule cures it (DESIGN.txt, "Order mix")."""
from ashfall_app.engine import (
    BP, HANDS, AfterTime, AtLeast, AtMost, CardCount, CardDef, CardId, ChipDef, ChipId, Flow, LaneId, LaneSpeed,
    LineKey, MixId, Order, Outcome, QueueEntry, SetOrders, SetQueue, StandingDef, StoreDef, StoreId, StoreValue,
    SwitchMix, TapCard, ActionId, Rules, Save, advance, advance_logged, decide, explain_work, new_save,
)
from ashfall_app.engine import work as engine_work
from tests.cards_contract.cards_world import Q, lane, make, mul, rules, save_mix, tap, view_of, with_mix

Z, E = StoreId("z"), StoreId("e")
CD, M, R = CardId("cd"), CardId("m"), CardId("r")
GEN = ActionId("gen")
TIRED = ChipId("tired")
RACK = LaneId("rack")
SLOW = mul(LaneSpeed(HANDS), 5000, "tired")


def tap_cards() -> list[CardDef]:
    return [CardDef(CD, 100, makes=(Flow(Z, 3600),), lines=(LineKey("cd.tap"),)),
            CardDef(M, 100, makes=(Flow(Z, 1000),))]


def landed_at(s: Save, r: Rules, until: int) -> list[int]:
    return [ln.time for ln in advance_logged(s, r, until).lines if ln.key == "cd.tap"]


def test_a_chip_showing_mid_tap_slows_the_mix_after_it_not_the_tap():
    r = rules([StoreDef(Z, 1000 * Q, 0)], cards=tap_cards(), chips=[ChipDef(TIRED, AfterTime(50), (SLOW,), None, None)])
    s = tap(with_mix(new_save(r), r, 0, {M: BP}), r, 0, CD)
    assert landed_at(s, r, 400) == [100]
    mid = advance(s, r, 60)
    assert explain_work(mid, r, CD).per_hour == BP and make(mid, r, CD, Z).per_hour == 3600
    after = advance(s, r, 101)
    assert lane(after, HANDS).card is None
    e = make(after, r, M, Z)
    assert e.per_hour == 500 and [m.source for m in e.muls] == ["tired"]


def test_a_tap_started_under_a_chip_keeps_its_slower_speed_after_the_chip_clears():
    """e fills an item every 10 s from 0; tired shows while e is at most 3 items and clears at 6, at 60 s. A 100 s tap
    started tired shows 200 s and takes 200 s; its explain still names the chip after it clears."""
    r = rules([StoreDef(Z, 1000 * Q, 0), StoreDef(E, 100 * Q, 0)], cards=tap_cards(),
              standing=[StandingDef(GEN, makes=(Flow(E, 360 * Q),))],
              chips=[ChipDef(TIRED, AtMost(StoreValue(E), 3 * Q, 6 * Q), (SLOW,), None, None)])
    s = new_save(r)
    assert view_of(s, r, CD).tap_s == 200 and engine_work.tap_seconds(s, r, CD) == 200
    s = tap(s, r, 0, CD)
    later = advance(s, r, 120)
    assert not later.chips[0]
    w = explain_work(later, r, CD)
    assert w.per_hour == BP // 2 and [m.source for m in w.muls] == ["tired"]
    assert landed_at(s, r, 400) == [200]


def test_a_speed_entry_an_outcome_adds_mid_tap_applies_from_the_taps_end():
    """The rack's r lands at 50 and doubles the hands' speed: the hands' 100 s tap still lands at 100, and a tap after
    it runs at the doubled speed."""
    rack = CardDef(R, 50, lane=RACK, cap=1, outcome=Outcome(modifiers=(mul(LaneSpeed(HANDS), 20_000, "tool"),)))
    r = rules([StoreDef(Z, 1000 * Q, 0)], cards=[*tap_cards(), rack], lanes=[RACK])
    s = tap(tap(new_save(r), r, 0, R), r, 0, CD)
    assert landed_at(s, r, 400) == [100]
    assert engine_work.tap_seconds(advance(s, r, 100), r, CD) == 50


def _tired_queue(rule: bool) -> tuple[Rules, Save]:
    """e drains 7 items over the 100 s tap of cd and reaches 3 at its landing, so tired (at most 3, clear at 6) shows as
    the hands free; rest refills an item a second. The queue holds one tap of m; with `rule`, "While tired → Rest"."""
    cond = AtMost(StoreValue(E), 3 * Q, 6 * Q)
    rest = CardId("rest")
    r = rules([StoreDef(E, 10 * Q, 10 * Q), StoreDef(Z, 1000 * Q, 0)],
              cards=[*tap_cards(), CardDef(rest, 10, makes=(Flow(E, Q),))],
              standing=[StandingDef(GEN, costs=(Flow(E, 7 * Q // 100),))],
              chips=[ChipDef(TIRED, cond, (SLOW,), None, None)])
    s = new_save(r)
    if rule:
        s = save_mix(s, r, 0, {rest: BP}, "rest")
        s = decide(s, r, 0, SetOrders((Order(cond, SwitchMix(MixId("rest"))),)))
    s = tap(s, r, 0, CD)
    return r, decide(s, r, 0, SetQueue((QueueEntry(TapCard(M), AtLeast(CardCount(M), 1, 1)),)))


def test_the_queue_head_waits_for_a_chips_rule_to_cure_it_then_starts_at_full_speed():
    """With the rule, the hands free tired at 100: the rule's mix runs, the queue's m waits, and m starts the instant
    tired clears, at full speed. With no rule nothing would cure it: m starts at 100 at the tired speed."""
    r, s = _tired_queue(rule=True)
    at = advance(s, r, 100)
    assert at.chips == (True,) and lane(at, HANDS).card is None
    clear = next(t for t in range(100, 200) if not advance(s, r, t).chips[0])
    assert lane(advance(s, r, clear - 1), HANDS).card is None
    started = advance(s, r, clear)
    assert lane(started, HANDS).card == M and explain_work(started, r, M).per_hour == BP
    r, s = _tired_queue(rule=False)
    at = advance(s, r, 100)
    assert lane(at, HANDS).card == M and explain_work(at, r, M).per_hour == BP // 2
