"""The cards decisions of DESIGN.txt, part "CARDS", each on a small world: landing at the boundary, a tap whose speed
is 0, the evaluation after a cascade, dead queue entries, the run precedence, the store-once and requires validation,
and a pause that outlives its tap."""
from dataclasses import replace
from collections.abc import Callable

import pytest

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, ActionId, Amount, AfterTime, AtLeast, AtMost, CapRaise, CardDef, CardId, CardShare,
    ChipDef, ChipId, EventKind, Flow, InvalidRulesError, InvalidVerbError, LaneSpeed, LineKey, Mix, MixId, Modifier,
    ModifierKind, Order, Outcome, PacingCurve, QueueEntry, Rules, Running, RunKind, SaveMix, SetOrders, SetQueue,
    SkillDef, SkillId, SourceId, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, advance,
    advance_logged, decide, explain_work, new_save, next_event, validate_rules, view,
)
from ashfall_app.engine import Save

X, Z = StoreId("x"), StoreId("z")
C, D, S, B = CardId("c"), CardId("d"), CardId("s"), CardId("b")


def world(cards: list[CardDef], stores: list[StoreDef] | None = None, standing: list[StandingDef] | None = None,
          chips: list[ChipDef] | None = None, max_firings: int = 1000) -> Rules:
    r = Rules(stores=tuple(stores or [StoreDef(X, 100 * Q, Q), StoreDef(Z, 100 * Q)]), skills=(SkillDef(SkillId("k")),),
              standing=tuple(standing or []), curve=PacingCurve((10**9 * Q,)), cards=tuple(cards),
              chips=tuple(chips or []), max_firings_per_instant=max_firings)
    validate_rules(r)
    return r


def lines(r: Rules, s: Save, t: int) -> list[tuple[int, str]]:
    return [(ln.time, ln.key) for ln in advance_logged(s, r, t).lines]


def mix(r: Rules, s: Save, t: int, shares: dict[CardId, int]):
    s = decide(s, r, t, SaveMix(Mix(MixId("m"), tuple(CardShare(c, b) for c, b in shares.items()))))
    return decide(s, r, t, SwitchMix(MixId("m")))


def test_a_tap_landing_as_its_input_runs_out_lands():
    """x holds exactly c's input, so it reaches 0 at the second the work reaches the boundary: the landing stands (its
    line, the lane freed) and the card is not paused."""
    r = world([CardDef(C, 100, inputs=(Amount(X, Q),), lines=(LineKey("c.tap"),))])
    s = decide(new_save(r), r, 0, TapCard(C))
    step = advance_logged(s, r, 100)
    assert [(ln.time, ln.key) for ln in step.lines] == [(100, "c.tap")]
    assert step.save.pauses == () and step.save.lanes[0].card is None
    assert next(cs.work.start_value for cs in step.save.cards) == 100 * BP


def test_the_dry_rule_passes_over_a_landing_card_and_pauses_the_rest():
    """Two consumers of x, one landing at the instant x runs out: the other is paused, the landing one is not."""
    fire = ActionId("fire")
    r = world([CardDef(C, 100, inputs=(Amount(X, Q),), lines=(LineKey("c.tap"),))],
              stores=[StoreDef(X, 100 * Q, 2 * Q)], standing=[StandingDef(fire, costs=(Flow(X, 36_000),))])
    a = advance(decide(new_save(r), r, 0, TapCard(C)), r, 100)
    assert [p.runner for p in a.pauses] == [fire] and a.lanes[0].card is None


def test_a_tap_at_speed_zero_is_refused_and_a_hands_tap_keeps_its_start_speed():
    """A speed of 0 at the start refuses the tap; a chip stopping the hands mid-tap leaves the tap at its start speed
    to its landing (DESIGN.txt, "Speed")."""
    slow = Modifier(LaneSpeed(HANDS), ModifierKind.MUL_BP, 0, SourceId("tired"))
    r = world([CardDef(C, 100, lines=(LineKey("c.tap"),))])
    s = new_save(r, (slow,))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, TapCard(C))
    stopped = decide(decide(s, r, 0, SetOrders((Order(AfterTime(0), TapCard(C)),))), r, 0, SetOrders(()))
    assert stopped.lanes[0].card is None and stopped.cards == ()

    tired = ChipDef(ChipId("tired"), AfterTime(50), (replace(slow, source=SourceId("tired")),))
    r = world([CardDef(C, 100, lines=(LineKey("c.tap"),))], chips=[tired])
    s = decide(new_save(r), r, 0, TapCard(C))
    a = advance_logged(s, r, 50)
    assert a.save.lanes[0].card == C and a.lines == ()
    assert a.save.cards[0].work.start_value == 50 * BP and a.save.cards[0].work.rate == BP
    assert [ln.key for ln in advance_logged(s, r, 100).lines] == ["c.tap"]


def test_a_cascade_leaves_the_ready_card_a_ready_event_one_second_on():
    """With two firings allowed per instant, the completion and landing at 10 suspend evaluation; READY at 11 taps
    again."""
    r = world([CardDef(C, 10, cap=5)], max_firings=2)
    s = decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(C)),)))
    assert s.lanes[0].card == C
    a = advance(s, r, 10)
    assert a.lanes[0].card is None and a.last_cascade is not None and a.last_cascade.time == 10
    ev = next_event(a, r)
    assert ev is not None and (ev.time, ev.kind) == (11, EventKind.READY)
    assert advance(a, r, 11).lanes[0].card == C


@pytest.mark.parametrize("cap", [99_999, 100_000])
def test_a_chain_that_repeats_reaches_a_large_cap_at_the_cost_of_one_period(cap: int):
    """Two mix orders flip on whether c runs, which each one's mix changes: the chain repeats with period 2 until the
    cap, so the result is the cap's (cap firings, the running mix by its parity) and, the period skipped, it settles
    well inside the per-test ceiling; run firing by firing it takes far longer."""
    r = world([CardDef(C, 60, makes=(Flow(X, 1000),))], max_firings=cap)
    run, stop = MixId("run"), MixId("stop")
    s = decide(decide(new_save(r), r, 0, SaveMix(Mix(run, (CardShare(C, BP),)))), r, 0, SaveMix(Mix(stop, ())))
    s = decide(s, r, 0, SwitchMix(run))
    s = decide(s, r, 0, SetOrders((Order(AtLeast(Running(C), 1, 1), SwitchMix(stop)),
                                   Order(AtMost(Running(C), 0, 0), SwitchMix(run)))))
    assert view(s, r).running_mix == (stop if cap % 2 == 0 else run)
    assert s.cascade_count == 1 and s.last_cascade is not None and (s.last_cascade.time, s.last_cascade.firings) == (0, cap)


def test_a_dead_queue_entry_stays_and_the_first_live_entry_pops():
    r = world([CardDef(S, 10, cap=1), CardDef(C, 10)])
    s = mix(r, new_save(r), 0, {S: BP})
    s = advance(s, r, 10)
    assert view(s, r).completed
    wait = QueueEntry(TapCard(S), AtLeast(StoreValue(Z), 0, 0))  # holds, and could fall
    s = decide(s, r, 10, SetQueue((wait, QueueEntry(TapCard(C), AfterTime(30)))))
    assert s.queue[0] == wait and s.lanes[0].card == C
    assert next_event(s, r) is not None
    a = advance(s, r, 30)
    assert a.queue == (wait,)


def test_a_revived_dead_entry_pops_at_once_when_its_until_holds():
    r = world([CardDef(S, 10, cap=1), CardDef(D, 5, cap=1, outcome=Outcome(raises=(CapRaise(S, 1),)))])
    s = advance(mix(r, new_save(r), 0, {S: BP}), r, 10)
    s = decide(s, r, 10, SetQueue((QueueEntry(TapCard(S), AtLeast(StoreValue(Z), 0, 0)),)))
    assert len(s.queue) == 1
    a = advance(decide(s, r, 10, TapCard(D)), r, 15)
    assert a.queue == () and a.lanes[0].card is None


def test_a_greyed_card_reads_greyed_before_waiting_and_a_stopped_mix_card_explains_through_its_share():
    r = world([CardDef(S, 10, cap=1), CardDef(B, 10, requires=(AtLeast(StoreValue(Z), Q, Q),))])
    s = mix(r, new_save(r), 0, {S: 5000, B: 5000})
    cv = {c.card: c for c in view(s, r).cards}
    assert cv[B].run is RunKind.WAITING
    a = advance(s, r, 20)
    cv = {c.card: c for c in view(a, r).cards}
    assert cv[B].run is RunKind.GREYED and cv[B].share_bp == 5000
    e = explain_work(a, r, B)
    assert e.share_bp == 5000 and e.run.kind is RunKind.GREYED and e.per_hour == 0


def test_a_pause_outlives_the_tap_it_interrupted_and_blocks_a_new_tap():
    r = world([CardDef(C, 200, inputs=(Amount(X, Q),), lines=(LineKey("c.tap"),))],
              standing=[StandingDef(ActionId("fire"), costs=(Flow(X, 18_000),))])
    s = decide(new_save(r), r, 0, TapCard(C))
    a = advance(s, r, 100)
    assert a.lanes[0].card is None and C in [p.runner for p in a.pauses]
    card = view(a, r).cards[0]
    assert card.blocker is not None
    assert decide(a, r, 100, TapCard(C)) == a


_BAD_CARDS: list[Callable[[CardDef], CardDef]] = [
    lambda c: replace(c, makes=(Flow(Z, 5),), outcome=Outcome(stores=(Amount(Z, Q),))),
    lambda c: replace(c, costs=(Flow(X, 5),), inputs=(Amount(X, Q),)),
    lambda c: replace(c, makes=(Flow(Z, 5), Flow(Z, 6))),
    lambda c: replace(c, costs=(Flow(X, 5), Flow(X, 6))),
    lambda c: replace(c, inputs=(Amount(X, Q), Amount(X, Q))),
    lambda c: replace(c, requires=(AtLeast(StoreValue(Z), Q, Q - 1),)),
]


@pytest.mark.parametrize("bad", _BAD_CARDS)
def test_a_store_is_on_a_card_once_and_a_requires_is_a_plain_threshold(bad: Callable[[CardDef], CardDef]):
    with pytest.raises(InvalidRulesError):
        world([bad(CardDef(C, 10))])


def test_capped_and_uncapped_cards_complete_at_the_same_seconds():
    """At 15% a 100 s card takes 666.67 s: both cross at 667 and 1334, and the capped one lands its lines there."""
    r = world([CardDef(C, 100, cap=3, lines=(LineKey("a"), LineKey("b"), LineKey("c"))), CardDef(D, 100)])
    s = mix(r, new_save(r), 0, {C: 1500, D: 1500})
    assert lines(r, s, 2000) == [(667, "a"), (1334, "b"), (2000, "c")]
    for t in (666, 667, 1333, 1334):
        done = {cs.card: cs.work.start_value // (100 * BP) for cs in advance(s, r, t).cards}
        assert done[C] == done[D], t
