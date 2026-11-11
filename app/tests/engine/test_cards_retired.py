"""Retired cards (DESIGN.txt, CARDS, "Retired"): an Outcome unlocks Unlock(RETIRED, card) and the card is out of play
exactly as a completed one is. Tests written from that contract text."""
from typing import Literal

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, Amount, CardDef, CardId, CardShare, InvalidRulesError,
    InvalidVerbError, LaneDef, LaneId, Mix, MixId, Order, Outcome, PacingCurve, Rules, RateRef, FlowKind, RunKind,
    SaveMix, SetOrders, StoreDef, StoreId, TapCard, TriggerDef, TriggerId, AtLeast, StoreValue, SwitchMix,
    Unlock, UnlockKind, advance, decide, explain, new_save, validate_rules, value, view,
)

GOLD, COIN = StoreId("gold"), StoreId("coin")
OLD, NEW, OTHER, BENCH = CardId("old"), CardId("new"), CardId("other"), CardId("bench")
SHELF = LaneId("shelf")
RETIRE_OLD = Unlock(UnlockKind.RETIRED, "old")


def card_unlocks(*ids: CardId) -> tuple[Unlock, ...]:
    return tuple(Unlock(UnlockKind.CARD, c) for c in ids)


def world(*, retire_by: str | None = "card", opening: Literal["all"] | tuple[Unlock, ...] | None = "all", retired: str = "old", at: int = 30) -> Rules:
    """OLD (hands, gold) is replaced by NEW (a capped hands tap whose `finished` retires it) or by a trigger at t=30.
    BENCH runs on a second lane (work 100) and is retired by the same outcomes."""
    gone = Outcome(unlocks=(Unlock(UnlockKind.RETIRED, retired),))
    everyone = (OLD, NEW, OTHER, BENCH)
    r = Rules(
        stores=(StoreDef(GOLD, 100 * Q), StoreDef(COIN, 100 * Q)),
        skills=(), standing=(), curve=PacingCurve((10**9 * Q,)),
        lanes=(LaneDef(SHELF),),
        cards=(
            CardDef(OLD, 10, outcome=Outcome(stores=(Amount(GOLD, Q),))),
            CardDef(NEW, 5, cap=1, finished=gone if retire_by == "card" else Outcome()),
            CardDef(OTHER, 10, outcome=Outcome(stores=(Amount(COIN, Q),))),
            CardDef(BENCH, 100, lane=SHELF, outcome=Outcome(stores=(Amount(COIN, Q),))),
        ),
        triggers=(TriggerDef(TriggerId("t"), AfterTime(at), gone),) if retire_by == "trigger" else (),
        opening=card_unlocks(*everyone) if opening == "all" else opening,
    )
    validate_rules(r)
    return r


def with_mixes(r: Rules):
    s = new_save(r)
    s = decide(s, r, 0, SaveMix(Mix(MixId("uses_old"), (CardShare(OLD, BP),))))
    s = decide(s, r, 0, SaveMix(Mix(MixId("safe"), (CardShare(OTHER, BP),))))
    return s


def retired_save(by: str = "card"):
    """OLD retired while the active mix holds it; both mixes saved, nothing running afterwards but the mix."""
    r = world(retire_by=by)
    s = decide(with_mixes(r), r, 0, SwitchMix(MixId("uses_old")))
    if by == "card":
        s = decide(s, r, 0, TapCard(NEW))
        s = advance(s, r, 5)
    else:
        s = advance(s, r, 30)
    return r, s


@pytest.mark.parametrize("by", ["card", "trigger"])
def test_retiring_moves_the_card_to_completed_and_out_of_cards(by: str):
    r, s = retired_save(by)
    assert RETIRE_OLD in s.unlocked
    v = view(s, r)
    assert OLD in [c.card for c in v.completed]
    assert OLD not in [c.card for c in v.cards]


def test_control_without_the_retiring_outcome_the_card_stays_in_play():
    r = world(retire_by=None)
    s = decide(with_mixes(r), r, 0, SwitchMix(MixId("uses_old")))
    s = advance(decide(s, r, 0, TapCard(NEW)), r, 5)
    v = view(s, r)
    assert RETIRE_OLD not in s.unlocked
    assert OLD in [c.card for c in v.cards] and OLD not in [c.card for c in v.completed]
    assert v.greyed_mixes == ()
    decide(s, r, 5, TapCard(OLD))


@pytest.mark.parametrize("by", ["card", "trigger"])
def test_mix_holding_a_retired_card_greys_and_contributes_nothing(by: str):
    r, s = retired_save(by)
    v = view(s, r)
    assert v.greyed_mixes == (MixId("uses_old"),)
    gold = value(s, r, GOLD, 40)
    assert value(advance(s, r, 1000), r, GOLD, 1000) == gold
    assert explain(s, r, RateRef(OLD, FlowKind.MAKE, GOLD)).run.kind is RunKind.GREYED


def test_a_mix_with_other_cards_is_not_greyed_and_still_runs():
    r, s = retired_save("card")
    assert MixId("safe") not in view(s, r).greyed_mixes
    s = decide(s, r, 5, SwitchMix(MixId("safe")))
    assert value(advance(s, r, 25), r, COIN, 25) > value(s, r, COIN, 5)


@pytest.mark.parametrize("by", ["card", "trigger"])
def test_player_tap_of_a_retired_card_is_refused(by: str):
    r, s = retired_save(by)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 40, TapCard(OLD))


def test_order_tap_of_a_retired_card_changes_nothing():
    r, s = retired_save("card")
    s = decide(s, r, 5, SetOrders((Order(AtLeast(StoreValue(GOLD), 0, 0), TapCard(OLD)),)))
    assert all(lane.card is None for lane in s.lanes)
    assert OLD not in [c.card for c in s.cards if c.work.start_value or c.work.rate]


def test_save_mix_rejects_a_retired_card_but_accepts_one_without():
    r, s = retired_save("card")
    with pytest.raises(InvalidVerbError):
        decide(s, r, 5, SaveMix(Mix(MixId("again"), (CardShare(OLD, BP),))))
    s = decide(s, r, 5, SaveMix(Mix(MixId("fresh"), (CardShare(OTHER, BP),))))
    assert MixId("fresh") in [m.id for m in s.mixes]
    s = decide(s, r, 5, SwitchMix(MixId("fresh")))
    assert value(advance(s, r, 20), r, COIN, 20) > 0


def test_a_ready_tap_on_another_lane_ends_at_the_instant_work_kept_lane_free():
    r = world(retire_by="card", retired="bench")
    s = decide(new_save(r), r, 0, TapCard(BENCH))
    s = advance(s, r, 2)
    assert s.lanes[1].card == BENCH
    s = decide(s, r, 2, TapCard(NEW))
    s = advance(s, r, 7)  # NEW lands at 7, the bench is retired then
    assert all(lane.card is None for lane in s.lanes)
    work = next(c.work for c in s.cards if c.card == BENCH)
    assert work.start_value == 7 * BP and work.rate == 0  # the bench kept its seven seconds, then stood still
    assert BENCH in [c.card for c in view(s, r).completed]
    s = advance(s, r, 500)
    assert next(c.work.start_value for c in s.cards if c.card == BENCH) == 7 * BP


def test_a_ready_hands_tap_ends_when_a_trigger_retires_it():
    r = world(retire_by="trigger", at=4)  # OLD's tap would end at 10; the retirement lands mid-tap
    s = advance(decide(new_save(r), r, 0, TapCard(OLD)), r, 3)
    assert s.lanes[0].card == OLD
    s = advance(s, r, 4)
    assert s.lanes[0].card is None
    assert next(c.work.start_value for c in s.cards if c.card == OLD) == 4 * BP
    gold = value(s, r, GOLD, 4)  # the four seconds of work paid its share (rate form) and nothing more
    s = advance(s, r, 500)
    assert next(c.work.start_value for c in s.cards if c.card == OLD) == 4 * BP and value(s, r, GOLD, 500) == gold


def test_retirement_is_for_good():
    r, s = retired_save("card")
    s = advance(s, r, 5000)
    assert RETIRE_OLD in s.unlocked and OLD in [c.card for c in view(s, r).completed]


def test_validation_rejects_a_retired_unlock_of_an_unknown_card():
    with pytest.raises(InvalidRulesError):
        world(retire_by="card", retired="ghost")


def test_with_no_opening_nothing_is_retired():
    r = world(retire_by="card", opening=None)
    s = new_save(r)
    s = advance(decide(s, r, 0, TapCard(NEW)), r, 5)
    v = view(s, r)
    assert OLD in [c.card for c in v.cards] and OLD not in [c.card for c in v.completed]
    decide(s, r, 5, TapCard(OLD))
