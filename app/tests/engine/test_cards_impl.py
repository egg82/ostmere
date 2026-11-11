"""The cards part end to end on small rules: one bar, rate-form lumps, taps, failed taps, interrupts, caps,
greyed mixes, starved lines, the view and the codec (DESIGN.txt, part "CARDS")."""
import pytest

from ashfall_app.engine import (
    BP, FORMAT, QUANTITY_SCALE as Q, ActionId, Amount, AfterTime, AtLeast, CapRaise, CardCount, CardDef, CardId,
    CardShare, DeleteMix, EventKind, Flow, InvalidRulesError, InvalidVerbError, LineKey, Mix, MixId, Order,
    Outcome, PacingCurve, QueueEntry, RateRef, FlowKind, Rules, RunBy, RunKind, SaveMix, SetOrders, SetQueue, SkillDef,
    SkillId, StandingDef, StateFormatError, StoreDef, StoreId, StoreValue, SubMix, SwitchMix, TapCard, TriggerDef,
    TriggerId, Unlock, UnlockKind, advance, advance_logged, decide, decide_logged, decode, encode, explain, explain_work,
    new_save, next_event, validate_rules, value, view,
)
from ashfall_app.engine import Save
from ashfall_app.engine.plan import running_mix_id

WOOD, PLANK = StoreId("wood"), StoreId("plank")
CHOP, CRAFT, STORY = CardId("chop"), CardId("craft"), CardId("story")


def rules(wood: int = 4, standing: tuple[StandingDef, ...] = (), triggers: tuple[TriggerDef, ...] = ()) -> Rules:
    r = Rules(
        stores=(StoreDef(WOOD, 100 * Q, wood * Q), StoreDef(PLANK, 100 * Q)),
        skills=(SkillDef(SkillId("k")),),
        standing=standing,
        curve=PacingCurve((10**9 * Q,)),
        cards=(
            CardDef(CHOP, 10, skill=SkillId("k"), xp_per_hour=1000, outcome=Outcome(stores=(Amount(WOOD, Q),)),
                    lines=(LineKey("chop.tap"),)),
            CardDef(CRAFT, 20, inputs=(Amount(WOOD, 2 * Q),), outcome=Outcome(stores=(Amount(PLANK, Q),)),
                    lines=(LineKey("craft.tap"),), failed_line=LineKey("craft.fail")),
            CardDef(STORY, 5, cap=3, lines=(LineKey("s1"), LineKey("s2"), LineKey("s3")),
                    finished=Outcome(lines=(LineKey("fin"),))),
        ),
        triggers=triggers,
    )
    validate_rules(r)
    return r


def mixed(r: Rules, *shares: tuple[CardId, int], name: str = "m"):
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId(name), tuple(CardShare(c, b) for c, b in shares))))
    return decide(s, r, 0, SwitchMix(MixId(name)))


def work(s: Save, card: CardId):
    return next((c.work.start_value for c in s.cards if c.card == card), 0)


def test_mix_share_fills_one_bar_and_lumps_run_as_rates():
    r = rules()
    s = mixed(r, (CHOP, 5000))
    s = advance(s, r, 20)
    assert work(s, CHOP) == 10 * BP and value(s, r, WOOD, 20) == 5 * Q
    v = view(s, r)
    assert v.cards[0].by is RunBy.MIX and v.cards[0].completions == 1 and v.cards[0].completes_at is None


def test_tap_yields_the_mix_and_resumes():
    r = rules()
    s = mixed(r, (CHOP, 5000))
    s = decide(s, r, 0, TapCard(CRAFT))
    e = explain(s, r, RateRef(CHOP, FlowKind.MAKE, WOOD))
    assert e.run.kind is RunKind.YIELDED and e.per_hour == 0 and e.share_bp == 5000
    assert view(s, r).cards[1].by is RunBy.TAP
    s = advance(s, r, 20)
    assert work(s, CRAFT) == 20 * BP and work(s, CHOP) == 0
    assert value(s, r, PLANK, 20) == Q and value(s, r, WOOD, 20) == 2 * Q
    assert view(s, r).lanes[0].card is None
    assert advance(s, r, 40).cards[0].work.start_value == 10 * BP


def test_tap_finishes_the_half_the_mix_left():
    r = rules()
    s = mixed(r, (CRAFT, 5000))
    s = advance(s, r, 20)  # half a bar
    assert work(s, CRAFT) == 10 * BP and value(s, r, WOOD, 20) == 3 * Q
    s = decide(s, r, 20, TapCard(CRAFT))
    assert view(s, r).cards[0].tap_s is not None
    s = advance(s, r, 30)
    assert work(s, CRAFT) == 20 * BP and value(s, r, WOOD, 30) == 2 * Q  # 2 paid once, never twice
    assert value(s, r, PLANK, 30) == Q


def test_tap_and_mix_move_stores_the_same_amount():
    r = rules()
    tapped = advance(decide(new_save(r), r, 0, TapCard(CRAFT)), r, 20)
    mixes = advance(mixed(r, (CRAFT, BP)), r, 20)
    for st in (WOOD, PLANK):
        assert abs(value(tapped, r, st, 20) - value(mixes, r, st, 20)) <= 1


def test_tap_line_lands_after_the_work_and_only_for_uncapped():
    r = rules()
    s = decide_logged(new_save(r), r, 0, TapCard(CHOP))
    done = advance_logged(s.save, r, 10)
    assert [(ln.time, ln.key) for ln in done.lines] == [(10, "chop.tap")]
    ev = next_event(s.save, r)
    assert ev is not None and ev.kind is EventKind.TAP_DONE


def test_a_failed_tap_costs_nothing_and_says_its_line_at_once():
    r = rules(wood=0)
    s = new_save(r)
    done = decide_logged(s, r, 0, TapCard(CRAFT))
    c = next(c for c in view(done.save, r).cards if c.card == CRAFT)
    assert c.blocker is not None and c.by is None and view(done.save, r).lanes[0].card is None
    assert [(ln.time, ln.key) for ln in done.lines] == [(0, "craft.fail")] and done.failed == CRAFT
    assert done.save == s and work(done.save, CRAFT) == 0


def test_busy_lane_and_unknown_card_refused_for_the_player_only():
    r = rules()
    s = decide(new_save(r), r, 0, TapCard(CHOP))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, TapCard(CRAFT))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, TapCard(CardId("nope")))


def test_dry_store_interrupts_a_tap_and_keeps_its_work():
    leak = StandingDef(ActionId("leak"), costs=(Flow(WOOD, 3600 * 1000),))  # one item a second
    r = rules(wood=3, standing=(leak,))
    s = decide(new_save(r), r, 0, TapCard(CRAFT))
    assert s.lanes[0].card == CRAFT
    done = advance_logged(s, r, 100)
    assert done.lines == () and done.save.lanes[0].card is None
    assert 0 < work(done.save, CRAFT) < 20 * BP


def test_capped_card_completions_are_events_with_lines_and_finish_once():
    r = rules()
    s = mixed(r, (STORY, BP))
    done = advance_logged(s, r, 100)
    assert [(ln.time, ln.key) for ln in done.lines] == [(5, "s1"), (10, "s2"), (15, "s3"), (15, "fin")]
    v = view(done.save, r)
    assert [c.card for c in v.completed] == [STORY] and v.greyed_mixes == (MixId("m"),) and v.cards[0].card == CHOP
    assert work(done.save, STORY) == 3 * 5 * BP


def test_tap_of_a_capped_card_completes_before_it_lands():
    r = rules()
    s = decide(new_save(r), r, 0, TapCard(STORY))
    done = advance_logged(s, r, 5)
    assert [ln.key for ln in done.lines] == ["s1"] and done.save.lanes[0].card is None


def test_completed_card_cannot_be_tapped_or_saved_and_raise_ungreys():
    raise_it = TriggerDef(TriggerId("t"),
                          AfterTime(100), Outcome(raises=(CapRaise(STORY, 2),)))
    r = rules(triggers=(raise_it,))
    s = advance(mixed(r, (STORY, BP)), r, 50)
    assert view(s, r).greyed_mixes == (MixId("m"),)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 50, TapCard(STORY))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 50, SaveMix(Mix(MixId("n"), (CardShare(STORY, 100),))))
    after = advance_logged(s, r, 120)
    assert [(ln.time, ln.key) for ln in after.lines] == [(105, "s3"), (110, "s3"), (110, "fin")]
    assert view(after.save, r).completed[0].completions == 5
    assert view(advance(s, r, 100), r).greyed_mixes == () and view(advance(s, r, 99), r).greyed_mixes != ()


def test_queue_skips_a_greyed_switch_and_keeps_it():
    r = rules()
    s = mixed(r, (STORY, BP))
    s = decide(s, r, 0, SaveMix(Mix(MixId("c"), (CardShare(CHOP, BP),))))
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(MixId("m")), AfterTime(10**6)),
                                  QueueEntry(SwitchMix(MixId("c")), AfterTime(10**6)))))
    s = advance(s, r, 30)
    assert running_mix_id(s, r) == "c" and len(s.queue) == 2
    s2 = decide(s, r, 30, DeleteMix(MixId("m"))) if False else s
    with pytest.raises(InvalidVerbError):
        decide(s2, r, 30, DeleteMix(MixId("m")))  # named by the queue


def test_delete_active_mix_evaluates():
    r = rules()
    s = mixed(r, (CHOP, BP))
    s = decide(s, r, 0, SetOrders((Order(AtLeast(StoreValue(WOOD), 0, 0), TapCard(CHOP)),)))
    s = decide(s, r, 5, DeleteMix(MixId("m")))
    assert s.active is None and s.lanes[0].card == CHOP


def test_starved_line_when_a_runner_waits_on_a_dry_store():
    r = rules(wood=0)
    s = mixed(r, (CRAFT, BP))
    s = advance(s, r, 1)
    ledger = {ln.store: ln for ln in view(s, r).ledger}
    assert ledger[WOOD].starved and not view(s, r).all_covered
    t = decide(new_save(r), r, 0, SetQueue((QueueEntry(TapCard(CRAFT), AfterTime(10**6)),)))
    assert {ln.store: ln for ln in view(t, r).ledger}[WOOD].starved


def test_order_on_card_count_fires_at_the_exact_second():
    r = rules()
    s = mixed(r, (CHOP, BP))
    s = decide(s, r, 0, SetOrders((Order(AtLeast(CardCount(CHOP), 3, 3), SwitchMix(MixId("m"))),)))
    ev = next_event(s, r)
    assert ev is not None and ev.time == 30 and ev.kind is EventKind.LATCH


def test_codec_round_trip_and_format():
    r = rules()
    s = advance(mixed(r, (CHOP, 3000), (CRAFT, 3000)), r, 123)
    assert decode(encode(s, r), r) == s and FORMAT == 9
    with pytest.raises(StateFormatError):
        decode(encode(s, r).replace('"format":9', '"format":8'), r)


def test_explain_work_names_the_share():
    r = rules()
    s = mixed(r, (CHOP, 4000))
    assert explain_work(s, r, CHOP).per_hour == 4000
    assert explain_work(s, r, CRAFT).per_hour == BP


def test_validation_of_cards():
    base = rules()
    bad = [
        CardDef(CardId("x"), 0), CardDef(CardId("x"), 1, cap=0), CardDef(CardId("x"), 1, lines=(LineKey("a"), LineKey("b"))),
        CardDef(CardId("x"), 1, finished=Outcome(lines=(LineKey("a"),))),
        CardDef(CardId("x"), 1, outcome=Outcome(unlocks=(Unlock(UnlockKind.CARD, "chop"),))),
        CardDef(CardId("x"), 1, makes=(Flow(WOOD, 1),), costs=(Flow(WOOD, 1),)),
        CardDef(CardId("x"), 2, cap=2, lines=(LineKey("a"),)),
        CardDef(CardId("x"), 1, lane=HANDS if False else __import__("ashfall_app.engine", fromlist=["LaneId"]).LaneId("zz")),
        CardDef(CardId("x"), 1, outcome=Outcome(raises=(CapRaise(CHOP, 1),))),
        CardDef(CardId("x"), 1, cap=1, outcome=Outcome(starts=(CHOP,))),
        CardDef(CHOP, 1),
    ]
    for c in bad:
        with pytest.raises(InvalidRulesError):
            validate_rules(Rules(base.stores, base.skills, base.standing, base.curve, cards=base.cards + (c,)))


def test_nested_mix_share_runs_the_flattened_card():
    r = rules()
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("in"), (CardShare(CHOP, BP),))))
    s = decide(s, r, 0, SaveMix(Mix(MixId("out"), (SubMix(MixId("in"), 5000),))))
    s = advance(decide(s, r, 0, SwitchMix(MixId("out"))), r, 20)
    assert work(s, CHOP) == 10 * BP


def test_requires_waits_a_mix_card_and_interrupts_a_tap():
    gated = CardDef(CardId("gate"), 10, requires=(AtLeast(StoreValue(PLANK), Q, Q),),
                    makes=(Flow(WOOD, 1000),))
    base = rules()
    r = Rules(base.stores, base.skills, base.standing, base.curve, cards=base.cards + (gated,))
    validate_rules(r)
    s = mixed(r, (CardId("gate"), BP), (CHOP, 0))
    run = view(s, r).cards[-1].run
    assert run is RunKind.WAITING and work(advance(s, r, 50), CardId("gate")) == 0
    s2 = mixed(r, (CardId("gate"), 5000), (CRAFT, 5000), name="n")
    # craft makes plank at 5000bp: its first plank lands as the bar fills, then the gate card starts
    late = advance(s2, r, 80)
    assert work(late, CardId("gate")) > 0


def test_dry_input_pauses_a_mix_card_and_resumes_when_refilled():
    r = rules(wood=1)
    s = mixed(r, (CRAFT, 5000), (CHOP, 5000))
    s = advance(s, r, 400)
    assert all(0 <= v.segment.start_value <= 100 * Q for v in view(s, r).ledger)
    assert work(s, CRAFT) > 0 and work(s, CHOP) > 0
    assert advance(advance(s, r, 450), r, 900) == advance(s, r, 900)
