"""The engine end to end: events, dry stores, caps, orders, the queue, the cascade cap, and the invariants
that make splitting time harmless."""
import pytest

from ashfall_app.engine import (
    AfterTime, AtLeast, AtMost, CardDef, CardId, CardShare, CascadeLimit, EventKind, Flow, FlowKind,
    InvalidVerbError, Mix, MixId, Order, PacingCurve, QueueEntry, RateRef, Rules, RunKind, Save, SaveMix, SetOrders,
    SetQueue, SkillDef, SkillId, SkillLevel, StoreDef, StoreId, StoreValue, SwitchMix, TimeOrderError, advance,
    decide, explain, level, new_save, next_event, per_hour, segment, units, validate_rules, value, value_at, view, xp,
)
from ashfall_app.engine.plan import running_mix_id

CANDLES, KNOWLEDGE, WOOD = StoreId("candles"), StoreId("knowledge"), StoreId("wood")
ARCANA, SCAV = SkillId("arcana"), SkillId("scav")
STUDY, SCAVENGE, CHOP = CardId("study"), CardId("scavenge"), CardId("chop")


def rules(max_firings: int = 1000) -> Rules:
    r = Rules(
        stores=(StoreDef(CANDLES, units(50), units(10)), StoreDef(KNOWLEDGE, units(20)), StoreDef(WOOD, units(100))),
        skills=(SkillDef(ARCANA), SkillDef(SCAV)),
        standing=(),
        cards=(
            CardDef(STUDY, 60, skill=ARCANA, xp_per_hour=per_hour(100), makes=(Flow(KNOWLEDGE, per_hour(2)),),
                    costs=(Flow(CANDLES, per_hour(4)),)),
            CardDef(SCAVENGE, 60, skill=SCAV, xp_per_hour=per_hour(50), makes=(Flow(CANDLES, per_hour(3)),)),
            CardDef(CHOP, 60, skill=SCAV, xp_per_hour=per_hour(10), makes=(Flow(WOOD, per_hour(10)),)),
        ),
        curve=PacingCurve((units(100), units(300), units(600))),
        max_firings_per_instant=max_firings,
    )
    validate_rules(r)
    return r


R = rules()


def running(*shares: tuple[CardId, int], r: Rules = R) -> Save:
    mix = Mix(MixId("m"), tuple(CardShare(a, s) for a, s in shares))
    s = decide(new_save(r), r, 0, SaveMix(mix))
    return decide(s, r, 0, SwitchMix(MixId("m")))


def event_times(save: Save, r: Rules, until: int) -> list[int]:
    times: list[int] = []
    while (e := next_event(save, r)) is not None and e.time <= until:
        times.append(e.time)
        save = advance(save, r, e.time)
    return times


def assert_splits(save: Save, r: Rules, end: int) -> None:
    """Invariant 1: any split, including at event times and one second either side, and a long chain of splits."""
    direct = advance(save, r, end)
    points = sorted({p for t in event_times(save, r, end) for p in (t - 1, t, t + 1) if save.time <= p <= end})
    for p in points:
        assert advance(advance(save, r, p), r, end) == direct, p
    chained = save
    for p in points + [end]:
        chained = advance(chained, r, p)
    assert chained == direct


def test_a_store_empties_at_the_exact_second_and_its_consumer_pauses():
    s = running((STUDY, 10_000))
    study = RateRef(STUDY, FlowKind.MAKE, KNOWLEDGE)
    assert explain(advance(s, R, 8999), R, study).run.kind is RunKind.FULL
    assert value(s, R, CANDLES, 8999) == units(10) - 8999 * 4000 > 0
    later = advance(s, R, 9000)
    assert value(later, R, CANDLES, 9000) == 0
    assert explain(later, R, study).run.kind is RunKind.PAUSED
    assert segment(later, R, KNOWLEDGE).rate == 0 and next_event(later, R) is None
    assert value(s, R, KNOWLEDGE, 10**6) == 9000 * 2000  # knowledge stopped with the candles


def test_dry_pause_and_resume_sawtooth_splits_cleanly():
    s = running((STUDY, 5000), (SCAVENGE, 5000))
    assert segment(s, R, CANDLES).rate == 1500 - 2000
    cost = RateRef(STUDY, FlowKind.COST, CANDLES)
    assert value(s, R, CANDLES, 71_999) > 0 and value(s, R, CANDLES, 72_000) == 0
    # paused, study's share goes to scavenge, which refills an hour of study's cost at 3000 a second: 2400 s
    kinds = [explain(advance(s, R, t), R, cost).run.kind for t in (71_999, 72_000, 74_399, 74_400, 88_799, 88_800)]
    assert kinds == [RunKind.FULL, RunKind.PAUSED, RunKind.PAUSED, RunKind.FULL, RunKind.FULL, RunKind.PAUSED]
    cur = s  # samples chain forward (equal to advancing from s by invariant 1) so the walk stays linear
    for t in range(0, 300_000, 977):
        cur = advance(cur, R, t)
        assert segment(cur, R, CANDLES).start_value >= 0
    assert_splits(s, R, 100_000)  # spans the first dry (72_000), resume (74_400) and re-dry (88_800)


def test_switching_while_a_store_is_empty_re_pauses_at_once():
    s = advance(running((STUDY, 10_000)), R, 10_000)  # candles empty since 9000, study paused
    s = decide(s, R, 10_000, SaveMix(Mix(MixId("other"), (CardShare(STUDY, 5000), CardShare(CHOP, 5000)))))
    s = decide(s, R, 10_000, SwitchMix(MixId("other")))  # clears pauses; candles still 0 with study costing them
    cost = RateRef(STUDY, FlowKind.COST, CANDLES)
    assert explain(s, R, cost).run.kind is RunKind.PAUSED and segment(s, R, CANDLES).rate == 0
    assert value(s, R, CANDLES, 20_000) == 0

def test_a_cap_stops_the_store_and_the_maker_keeps_training():
    s = running((CHOP, 10_000))
    assert value(s, R, WOOD, 36_000) == units(100)
    assert value(s, R, WOOD, 99_000) == units(100)
    assert xp(s, R, SCAV, 72_000) == 72_000 * per_hour(10)
    assert_splits(s, R, 80_000)


def test_explain_sums_to_the_store_rate():
    s = running((STUDY, 5000), (SCAVENGE, 5000))
    make = explain(s, R, RateRef(SCAVENGE, FlowKind.MAKE, CANDLES)).per_hour
    cost = explain(s, R, RateRef(STUDY, FlowKind.COST, CANDLES)).per_hour
    assert segment(s, R, CANDLES).rate == make - cost == -500
    assert explain(s, R, RateRef(CHOP, FlowKind.MAKE, WOOD)).share_bp == 0


def two_mixes(r: Rules = R) -> Save:
    s = new_save(r)
    s = decide(s, r, 0, SaveMix(Mix(MixId("study"), (CardShare(STUDY, 10_000),))))
    s = decide(s, r, 0, SaveMix(Mix(MixId("scav"), (CardShare(SCAVENGE, 10_000),))))
    return decide(s, r, 0, SwitchMix(MixId("study")))


def test_orders_with_hysteresis_keep_a_store_in_its_band():
    s = decide(two_mixes(), R, 0, SetOrders((
        Order(AtMost(StoreValue(CANDLES), units(2), units(8)), SwitchMix(MixId("scav"))),
        Order(AtLeast(StoreValue(CANDLES), units(8), units(8)), SwitchMix(MixId("study"))),
    )))
    seen: set[MixId | None] = set()
    cur = s  # samples chain forward (equal to advancing from s by invariant 1) so the walk stays linear
    for t in range(1800, 400_000, 1013):  # candles start at 10 and enter the band at 8 (t=1800)
        cur = advance(cur, R, t)
        v = segment(cur, R, CANDLES).start_value
        assert units(2) - 4000 <= v <= units(8) + 3000, (t, v)
        seen.add(running_mix_id(cur, R))
        assert cur.active == MixId("study")  # an order's mix runs over the player's, never replacing it
    assert seen == {MixId("study"), MixId("scav")}
    assert_splits(s, R, 30_000)  # two switches each way: to scav at 7_200 and 19_800, to study at 14_400 and 27_000


def test_queue_runs_in_order_and_orders_interrupt_only_at_latch_changes():
    s = decide(two_mixes(), R, 0, SwitchMix(MixId("scav")))
    s = decide(s, R, 10, SetQueue((
        QueueEntry(SwitchMix(MixId("scav")), AtLeast(StoreValue(CANDLES), units(20), units(20))),
        QueueEntry(SwitchMix(MixId("study")), AfterTime(10**9)),
    )))
    assert running_mix_id(advance(s, R, 11_999), R) == MixId("scav")
    assert running_mix_id(advance(s, R, 12_000), R) == MixId("study")  # 10 more units at 3/h from t=0
    assert len(advance(s, R, 12_000).queue) == 1


def test_level_conditions_and_levels():
    s = decide(two_mixes(), R, 0, SetOrders((Order(AtLeast(SkillLevel(ARCANA), 2, 2), SwitchMix(MixId("scav"))),)))
    # 100 xp/h at a 100% share reaches level 2 (100 units) at 3600 s
    assert level(s, R, ARCANA, 3599) == 1 and level(s, R, ARCANA, 3600) == 2
    assert running_mix_id(advance(s, R, 3599), R) == MixId("study")
    assert running_mix_id(advance(s, R, 3600), R) == MixId("scav")


def test_cascade_cap_suspends_evaluation_and_time_moves_on():
    r = rules(max_firings=1)
    s = decide(two_mixes(r), r, 0, SetOrders((Order(AfterTime(100), SwitchMix(MixId("scav"))),)))
    after = advance(s, r, 200)
    assert (after.cascade_count, after.last_cascade) == (1, CascadeLimit(100, 1))
    # the latch event is the instant's one firing, and an order's mix runs while it is latched: no verb to suspend
    assert running_mix_id(after, r) == MixId("scav") and after.active == MixId("study")
    assert advance(after, r, 10**6).time == 10**6
    replayed = decide(after, r, 200, SetOrders(after.orders))  # the cap stops chains, not the player
    assert running_mix_id(replayed, r) == MixId("scav") and replayed.cascade_count == 1
    assert_splits(s, r, 300)


def test_reading_is_pure_and_now_is_idempotent():
    s = running((STUDY, 5000), (SCAVENGE, 5000))
    copy = s
    value(s, R, CANDLES, 99_999)
    xp(s, R, ARCANA, 5)
    explain(s, R, RateRef(STUDY, FlowKind.XP))
    next_event(s, R)
    assert s == copy and advance(s, R, s.time) == s
    later = advance(s, R, 80_000)
    assert advance(later, R, later.time) == later
    assert all(st.segment.start == later.time for st in later.stores)


def test_segments_are_exact_until_the_next_event():
    s = advance(running((STUDY, 5000), (SCAVENGE, 5000)), R, 74_000)
    e = next_event(s, R)
    assert e is not None and e.kind is EventKind.RESUME
    for t in range(s.time, e.time + 1, 97):
        assert value(s, R, CANDLES, t) == value_at(segment(s, R, CANDLES), t)


def test_decide_advances_first_and_time_only_moves_forward():
    s = running((STUDY, 5000), (SCAVENGE, 5000))
    verb = SwitchMix(MixId("m"))
    assert decide(s, R, 80_000, verb) == decide(advance(s, R, 80_000), R, 80_000, verb)
    with pytest.raises(TimeOrderError):
        advance(advance(s, R, 10), R, 5)


@pytest.mark.parametrize("verb", [
    SwitchMix(MixId("nope")),
    SaveMix(Mix(MixId("x"), (CardShare(STUDY, 6000), CardShare(SCAVENGE, 6000)))),
    SetOrders((Order(AtLeast(StoreValue(CANDLES), 5, 6), SwitchMix(MixId("study"))),)),
    SetOrders((Order(AtMost(StoreValue(CANDLES), 5, 4), SwitchMix(MixId("study"))),)),
    SetOrders((Order(AfterTime(5), SwitchMix(MixId("nope"))),)),
])
def test_invalid_verbs_are_rejected(verb: SwitchMix | SaveMix | SetOrders):
    with pytest.raises(InvalidVerbError):
        decide(two_mixes(), R, 0, verb)


def test_a_rule_mix_runs_with_its_runs_out_at():
    """"Order mix": an order's mix is the running one, so runs_out_at reads its costs, while the player's own mix
    (scav, which costs nothing) waits underneath."""
    s = new_save(R)
    s = decide(s, R, 0, SaveMix(Mix(MixId("bare"), (CardShare(STUDY, 10_000),))))
    s = decide(s, R, 0, SaveMix(Mix(MixId("scav"), (CardShare(SCAVENGE, 10_000),))))
    s = decide(s, R, 0, SwitchMix(MixId("scav")))
    bare = decide(s, R, 0, SetOrders((Order(AfterTime(0), SwitchMix(MixId("bare"))),)))
    v = view(bare, R)
    assert v.running_mix == MixId("bare") and v.runs_out_at is not None and v.runs_out_at == 9000  # 10 at 4/h
