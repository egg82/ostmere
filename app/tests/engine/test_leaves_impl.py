"""A person leaves the town (engine DESIGN.txt, "LEAVES"): unit tests written beside the implementation. The contract
tests of invariants 148 to 155 are written blind elsewhere."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, AnswerDef, AnswerId, CardDef, CardId, CardShare, Ended, Flow,
    FlowKind, InvalidRulesError, InvalidVerbError, Join, LaneDef, LaneId, Leave, Mix, MixId, OfferDef, OfferId, Order,
    Outcome, PacingCurve, Pause, RateRef, Rules, Save, SaveMix, SetOrders, StandingDef, StoreDef, StoreId, TapCard, TriggerDef,
    TriggerId, Unlock, UnlockKind, advance, advance_logged, decide, decode, encode, explain, new_save,
    rebase_logged, rules_digest, validate_rules, view,
)
from ashfall_app.engine.joins import joined
from ashfall_app.engine.leaves import left

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
P1, P2 = LaneId("p1"), LaneId("p2")
A1, B1, C1, A2 = CardId("a1"), CardId("b1"), CardId("c1"), CardId("a2")
S = ActionId("s")
TOWN = MixId("town:main")
ALWAYS = AfterTime(0)
T = 1000


def world(leave: Leave | None = Leave(P1, (S,)), joins: bool = True) -> Rules:
    """Two people in one town mix (p1 with a1, b1 and a capped c1 paying z, p2 with a2), a standing action s, and p1
    leaving at T stopping s."""
    cards = (CardDef(A1, 100, lane=P1, makes=(Flow(X, Q),)), CardDef(B1, 100, lane=P1, makes=(Flow(Y, Q),)),
             CardDef(C1, 500, lane=P1, cap=3, outcome=Outcome(stores=(Amount(Z, 5 * Q),))),
             CardDef(A2, 100, lane=P2, makes=(Flow(X, 2 * Q),)))
    triggers = [TriggerDef(TriggerId("join"), AfterTime(0), Outcome(joins=(Join(P1, TOWN, A1), Join(P2, TOWN, A2))))]
    if leave is not None:
        triggers.append(TriggerDef(TriggerId("leave"), AfterTime(T), Outcome(leaves=(leave,))))
    r = Rules(stores=tuple(StoreDef(s, 10**6 * Q, 0) for s in (X, Y, Z)), skills=(),
              standing=(StandingDef(S, makes=(Flow(Y, Q),)),), curve=PacingCurve((10**9 * Q,)),
              lanes=(LaneDef(P1, True), LaneDef(P2, True)), cards=cards, triggers=tuple(triggers) if joins else ())
    validate_rules(r)
    return r


def store(s: Save, which: StoreId) -> int:
    return next(st.segment.start_value for st in s.stores if st.store == which)


def planned(r: Rules) -> Save:
    """The town mix with b1 beside a1 at half each, and rules tapping b1 and c1."""
    s = advance(new_save(r), r, 1)
    s = decide(s, r, 1, SaveMix(Mix(TOWN, (CardShare(A1, BP // 2), CardShare(A2, BP), CardShare(B1, BP // 2)))))
    rules = (*s.orders, Order(AfterTime(2000), TapCard(B1)), Order(AfterTime(5000), TapCard(C1)),
             Order(AfterTime(6000), TapCard(A2)))
    return decide(s, r, 1, SetOrders(rules))


def test_the_lane_goes_logged_and_nobody_else_changes():
    r = world()
    s = planned(r)
    before = advance(s, r, T - 1)
    step = advance_logged(s, r, T + 10)
    after = step.save
    assert Unlock(UnlockKind.LEFT, P1) in after.unlocked
    assert after.mixes == (Mix(TOWN, (CardShare(A2, BP),)),)
    assert [o.then for o in after.orders if isinstance(o.then, TapCard)] == [TapCard(A2)]
    ended = [c for c in step.rule_changes if c.ended is not None]
    assert [(c.time, c.order.then, c.ended, c.on) for c in ended] == [
        (T, TapCard(B1), Ended.LEFT, False), (T, TapCard(C1), Ended.LEFT, False)]
    assert explain(after, r, RateRef(A2, FlowKind.MAKE, X)) == explain(before, r, RateRef(A2, FlowKind.MAKE, X))
    v = view(after, r)
    assert v.greyed_mixes == () and v.running_town_mix == TOWN
    assert [b.lane for b in v.lanes] == ["hands", P2]
    assert {c.card for c in v.cards} == {A2} and v.completed == ()
    assert [b.action for b in v.standing] == []
    assert explain(after, r, RateRef(S, FlowKind.MAKE, Y)).share_bp == 0
    assert explain(before, r, RateRef(S, FlowKind.MAKE, Y)).share_bp == BP


def test_a_task_under_way_pays_nothing_more_and_never_completes():
    r = world()
    s = advance(new_save(r), r, 1)
    s = decide(s, r, 1, SetOrders((Order(AfterTime(T - 100), TapCard(C1)),)))
    at = advance(s, r, T)
    paid = store(at, Z)
    assert paid == store(advance(s, world(leave=None), T), Z) and 0 < paid < 5 * Q and at.lanes[1].card is None
    later = advance(s, r, T + 5000)
    assert store(later, Z) == paid
    assert next(cs.work.start_value for cs in later.cards if cs.card == C1) == 100 * BP


def test_the_lane_is_out_of_play_for_the_player():
    r = world()
    s = advance(planned(r), r, T + 1)
    with pytest.raises(InvalidVerbError):
        decide(s, r, T + 1, TapCard(B1))
    with pytest.raises(InvalidVerbError):
        decide(s, r, T + 1, SaveMix(Mix(MixId("town:other"), (CardShare(A1, BP),))))
    kept = decide(s, r, T + 1, SetOrders((*s.orders, Order(ALWAYS, TapCard(A1)))))
    assert advance(kept, r, T + 500).lanes[1].card is None


def test_a_second_leave_or_a_join_after_changes_nothing():
    r = world()
    s = advance(planned(r), r, T + 1)
    assert left(s, r, (Leave(P1),)) is s
    alone = world(joins=False)
    gone = left(advance(new_save(alone), alone, 1), alone, (Leave(P1),))
    assert joined(gone, alone, (Join(P1, TOWN, A1),)) is gone


def test_validation():
    with pytest.raises(InvalidRulesError, match="not a declared ruled lane"):
        world(leave=Leave(LaneId("nowhere")))
    with pytest.raises(InvalidRulesError, match="stopping nope"):
        world(leave=Leave(P1, (ActionId("nope"),)))
    r = world()
    twice = replace(r, triggers=(*r.triggers, TriggerDef(TriggerId("again"), AfterTime(9), Outcome(leaves=(Leave(P1),)))))
    with pytest.raises(InvalidRulesError, match="left by two outcomes"):
        validate_rules(twice)
    card = replace(r, cards=(*r.cards, CardDef(CardId("h"), 10, cap=1, outcome=Outcome(leaves=(Leave(P2),)))))
    with pytest.raises(InvalidRulesError, match="has a person leave"):
        validate_rules(card)
    for unlocks in ((Outcome(unlocks=(Unlock(UnlockKind.LEFT, P1),)),), ()):
        bad = replace(r, triggers=(*r.triggers, TriggerDef(TriggerId("u"), AfterTime(9), unlocks[0])) if unlocks
                      else r.triggers, opening=None if unlocks else (Unlock(UnlockKind.LEFT, P1),))
        with pytest.raises(InvalidRulesError, match="left"):
            validate_rules(bad)
    offer = OfferDef(OfferId("o"), (AnswerDef(AnswerId("y"), Outcome(leaves=(Leave(P2),))), AnswerDef(AnswerId("n"))))
    validate_rules(replace(r, offers=(offer,)))


def test_codec_and_digest():
    r = world()
    s = advance(planned(r), r, T + 1)
    assert decode(encode(s, r), r) == s
    plain = world(leave=None)
    assert rules_digest(plain) == rules_digest(replace(r, triggers=plain.triggers))


def test_a_save_past_the_moment_rebased_into_rules_that_add_it_loads_with_the_person_gone():
    old, r = world(leave=None), world()
    s = advance(planned(old), old, T + 50)
    step = rebase_logged(encode(s, old), r)
    assert Unlock(UnlockKind.LEFT, P1) in step.save.unlocked
    assert step.save.mixes == (Mix(TOWN, (CardShare(A2, BP),)),)
    assert {(c.order.then, c.ended) for c in step.rule_changes if c.ended is not None} == {
        (TapCard(B1), Ended.LEFT), (TapCard(C1), Ended.LEFT)}
    view(advance(step.save, r, T + 9000), r)


def test_the_pauses_of_what_stopped_with_the_person_go_and_the_rest_stay():
    r = world(joins=False)
    s = advance(new_save(r), r, 1)
    paused = replace(s, pauses=(Pause(S, Y, 5), Pause(B1, Y, 5), Pause(A2, Y, 5)))
    assert left(paused, r, (Leave(P1, (S,)),)).pauses == (Pause(A2, Y, 5),)
