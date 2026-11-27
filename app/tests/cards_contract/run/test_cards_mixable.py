"""Only HANDS cards are mixable ("Mixable"); standing actions are unchanged by the cards part ("Standing", invariant 33);
running dry pauses consumers last first: other lanes, then HANDS, then standing actions; DeleteMix (invariant 42)."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, CardDef, CardId, CardShare, DeleteMix, Flow, InvalidVerbError, Mix, MixId, Order,
    QueueEntry, Rules, RunKind, SaveMix, SetOrders, SetQueue, StandingBar, StandingDef, StoreDef, StoreId, SubMix,
    SwitchMix, Unlock, UnlockKind, advance, decide, explain_work, new_save, view,
)
from cards_world import K, Q, RACK, cost, lane, make, rules, running_mix, save_mix, tap, val, with_mix, work

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
C, D, R, LOCKED = CardId("c"), CardId("d"), CardId("r"), CardId("locked")
FIRE, GEN = ActionId("fire"), ActionId("gen")
M0, M1, M2, OUTER = MixId("m0"), MixId("m1"), MixId("m2"), MixId("outer")


def world(opening: list[Unlock] | None = None):
    return rules([StoreDef(X, 100 * Q, 50 * Q), StoreDef(Y, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
                 standing=[StandingDef(FIRE, costs=(Flow(X, 2000),))],
                 cards=[CardDef(C, 100, makes=(Flow(Y, 1000),)), CardDef(D, 100, makes=(Flow(Z, 1000),)),
                        CardDef(R, 100, lane=RACK, makes=(Flow(Z, 1000),)), CardDef(LOCKED, 100)],
                 lanes=[RACK], opening=opening)


GATED = [*(Unlock(UnlockKind.STORE, s) for s in (X, Y, Z)), Unlock(UnlockKind.SKILL, K), Unlock(UnlockKind.ACTION, FIRE),
         *(Unlock(UnlockKind.CARD, c) for c in (C, D, R))]


@pytest.mark.parametrize("card, why", [(R, "a card on another lane"), (CardId(str(FIRE)), "a standing action"),
                                       (LOCKED, "a locked card"), (CardId("nope"), "an unknown id")])
def test_only_unlocked_hands_cards_are_mixable(card: CardId, why: str):
    """"Mixable": SaveMix rejects a card off HANDS, a standing action, a locked card and an unknown id
    (InvalidVerbError); the control, a mix of unlocked HANDS cards, saves."""
    r = world(GATED)
    s = new_save(r)
    save_mix(s, r, 0, {C: 5000, D: 5000})
    with pytest.raises(InvalidVerbError):
        save_mix(s, r, 0, {C: 5000, card: 5000})


def test_standing_actions_run_at_a_full_share_whatever_the_hands_do():
    """Invariant 33: an unlocked standing action runs at BP from time 0, outside the mix and every lane: unchanged by a
    mix, a tap on HANDS (it is not yielded) or a greyed mix; it shows as a StandingBar, FULL."""
    r = world()
    s = new_save(r)
    assert cost(s, r, FIRE, X).per_hour == 2000 and cost(s, r, FIRE, X).share_bp == BP
    for a in (with_mix(s, r, 0, {C: BP}), tap(with_mix(s, r, 0, {C: BP}), r, 0, D), tap(s, r, 0, R)):
        e = cost(a, r, FIRE, X)
        assert (e.share_bp, e.run.kind, e.per_hour) == (BP, RunKind.FULL, 2000)
        assert view(a, r).standing == (StandingBar(FIRE, RunKind.FULL),)
    assert val(advance(s, r, 100), r, X) == 50 * Q - 200_000


def test_a_locked_standing_action_does_not_run():
    """"Standing": the ACTION unlock gates a standing action."""
    r = world([u for u in GATED if u != Unlock(UnlockKind.ACTION, FIRE)])
    s = new_save(r)
    assert cost(s, r, FIRE, X).per_hour == 0 and view(s, r).standing == ()
    assert val(advance(s, r, 100), r, X) == 50 * Q


def dry_world(gen: int):
    """Three equal consumers of x: a standing action, a mix card on HANDS and a tap on the rack; gen refills x."""
    return rules([StoreDef(X, 100 * Q, Q)],
                 standing=[StandingDef(GEN, makes=(Flow(X, gen),)), StandingDef(FIRE, costs=(Flow(X, 36_000),))],
                 cards=[CardDef(C, 100, costs=(Flow(X, 36_000),)), CardDef(R, 1000, lane=RACK, costs=(Flow(X, 36_000),))],
                 lanes=[RACK])


def test_running_dry_pauses_the_rack_first():
    """"Standing", "Running dry": consumers pause last first in the order standing, HANDS, other lanes, and only until
    the net is >= 0. With gen at 72_000 the net is -36_000, x empties at 100 and pausing the rack tap is enough: the tap
    is interrupted (its lane free, its work kept), while the mix card and the fire keep running."""
    r = dry_world(72_000)
    s = tap(with_mix(new_save(r), r, 0, {C: BP}), r, 0, R)
    a = advance(s, r, 100)
    assert lane(a, RACK).card is None and work(a, R).start_value == 100 * BP
    assert cost(a, r, C, X).run.kind is RunKind.FULL and cost(a, r, FIRE, X).run.kind is RunKind.FULL


def test_running_dry_pauses_the_rack_tap_before_the_hands_tap():
    """"Inputs against a dry store": the order read backwards is standing, HANDS (the mix, then the tapped card), then
    other lanes. With a tap on HANDS and one on the rack each drawing x, and gen making as much as one of them, x
    empties at 50 and pausing the rack tap is enough: the hands tap keeps running."""
    r = rules([StoreDef(X, 100 * Q, Q // 2)], standing=[StandingDef(GEN, makes=(Flow(X, 36_000),))],
              cards=[CardDef(C, 200, costs=(Flow(X, 36_000),)), CardDef(R, 1000, lane=RACK, costs=(Flow(X, 36_000),))],
              lanes=[RACK])
    a = advance(tap(tap(new_save(r), r, 0, C), r, 0, R), r, 50)
    assert lane(a, RACK).card is None and lane(a, HANDS).card == C


def test_running_dry_pauses_hands_before_standing():
    """"Standing", "Running dry": with gen at 36_000 the net is -72_000; x empties at 50 and both the rack tap and then
    the mix card pause; the fire, a standing action, is paused last and so keeps running. View.standing lists the gen
    (a maker) and the fire, in rules order."""
    r = dry_world(36_000)
    a = advance(tap(with_mix(new_save(r), r, 0, {C: BP}), r, 0, R), r, 50)
    assert lane(a, RACK).card is None
    assert cost(a, r, C, X).run.kind is RunKind.PAUSED
    assert cost(a, r, FIRE, X).run.kind is RunKind.FULL
    assert view(a, r).standing == (StandingBar(GEN, RunKind.FULL), StandingBar(FIRE, RunKind.FULL))


def test_a_paused_standing_action_reads_paused_while_a_tap_holds_the_hands():
    """"Standing", View.standing: fire empties x at 50 and the dry rule pauses it (nothing else draws x); a tap of d on
    HANDS from 0 to 100 does not change that, nor does it yield the standing action."""
    r = rules([StoreDef(X, 100 * Q, Q // 2)], standing=[StandingDef(FIRE, costs=(Flow(X, 36_000),))],
              cards=[CardDef(D, 100)])
    a = advance(tap(new_save(r), r, 0, D), r, 60)
    assert lane(a, HANDS).card == D
    assert cost(a, r, FIRE, X).run.kind is RunKind.PAUSED and val(a, r, X) == 0
    assert view(a, r).standing == (StandingBar(FIRE, RunKind.PAUSED),)


def test_standing_lists_every_unlocked_action_makers_included_and_a_paused_one_reads_paused():
    """View.standing: every unlocked standing action, makers and consumers, in rules order; a locked one is absent; one
    the dry rule pauses reads PAUSED. Here x holds an item, gen makes half what fire burns, and a locked third action
    stays out."""
    ice = ActionId("ice")
    r = rules([StoreDef(X, 100 * Q, Q)],
              standing=[StandingDef(GEN, makes=(Flow(X, 18_000),)), StandingDef(FIRE, costs=(Flow(X, 36_000),)),
                        StandingDef(ice, costs=(Flow(X, 100),))],
              opening=[Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.SKILL, K), Unlock(UnlockKind.ACTION, GEN),
                       Unlock(UnlockKind.ACTION, FIRE)])
    s = new_save(r)
    assert view(s, r).standing == (StandingBar(GEN, RunKind.FULL), StandingBar(FIRE, RunKind.FULL))
    a = advance(s, r, 300)
    assert view(a, r).standing == (StandingBar(GEN, RunKind.FULL), StandingBar(FIRE, RunKind.PAUSED))


def mixes(r: Rules):
    """m0 {c} active, m1 {d}, m2 {d}, outer nesting m1."""
    s = save_mix(new_save(r), r, 0, {D: BP}, "m1")
    s = save_mix(s, r, 0, {D: BP}, "m2")
    s = decide(s, r, 0, SaveMix(Mix(OUTER, (SubMix(M1, 5000),))))
    return with_mix(s, r, 0, {C: BP}, "m0")


@pytest.mark.parametrize("name", ["unknown", "nested", "named-by-order", "named-by-queue"])
def test_delete_mix_refuses_what_something_still_names(name: str):
    """Invariant 42: DeleteMix of an unknown mix, one nested in another, or one an order or a queue entry names raises
    InvalidVerbError (the save unchanged: nothing is returned)."""
    r = world()
    s = mixes(r)
    if name == "named-by-order":
        s = decide(s, r, 0, SetOrders((Order(AfterTime(10**9), SwitchMix(M2)),)))
    if name == "named-by-queue":
        s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(M2), AfterTime(10**9)),)))
    target = {"unknown": MixId("nope"), "nested": M1}.get(name, M2)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 10, DeleteMix(target))


def test_delete_mix_removes_a_mix_nothing_names():
    """Invariant 42: the mix is gone and the active one unchanged."""
    r = world()
    a = decide(mixes(r), r, 10, DeleteMix(M2))
    assert [m.id for m in a.mixes] == [M1, OUTER, M0] and a.active == M0


def test_deleting_the_active_mix_leaves_none_active():
    """Invariant 42, Save.active: deleting the active mix leaves no mix active; nothing runs on HANDS."""
    r = world()
    a = decide(mixes(r), r, 10, DeleteMix(M0))
    assert a.active is None and make(a, r, C, Y).per_hour == 0 and work(a, C).rate == 0


def test_deleting_another_mix_does_not_evaluate():
    """Invariant 42, DeleteMix, with "Order mix": an order's mix runs over the player's while it is latched; a player's
    switch then sets only the mix that comes back, and deleting an unrelated mix changes neither."""
    r = world()
    s = decide(mixes(r), r, 0, SetOrders((Order(AfterTime(0), SwitchMix(M1)),)))
    assert running_mix(s, r) == M1 and s.active == M0
    s = decide(s, r, 5, SwitchMix(OUTER))
    assert running_mix(s, r) == M1 and s.active == OUTER
    a = decide(s, r, 10, DeleteMix(M2))
    assert running_mix(a, r) == M1 and a.active == OUTER


def test_deleting_the_active_mix_under_a_queue_mix_leaves_the_queue_mix_running():
    """Invariant 42, DeleteMix, "Queue mix": the player's switch under the queue's m2 sets save.active alone; deleting
    that mix leaves nothing active and m2 running."""
    r = world()
    s = decide(mixes(r), r, 0, SetQueue((QueueEntry(SwitchMix(M2), AfterTime(10**9)),)))
    assert running_mix(s, r) == M2
    s = decide(s, r, 5, SwitchMix(M0))
    assert s.active == M0 and running_mix(s, r) == M2
    a = decide(s, r, 10, DeleteMix(M0))
    assert a.active is None and running_mix(a, r) == M2


def test_explain_work_follows_whoever_runs_the_card():
    """api.explain_work: share BP for a tap, the mix share otherwise; a card nobody runs explains as a tap now."""
    r = world()
    s = with_mix(new_save(r), r, 0, {C: 2500})
    assert explain_work(s, r, C).share_bp == 2500 and explain_work(s, r, C).per_hour == 2500
    assert explain_work(s, r, D).share_bp == BP and explain_work(s, r, D).per_hour == BP
    t = tap(s, r, 0, C)
    assert explain_work(t, r, C).share_bp == BP and work(t, C).rate == BP
    assert lane(t, HANDS).card == C


def test_mix_shares_are_of_cards():
    """mixes.CardShare: a saved mix holds cards, flattening as before (a SubMix scales the inner shares once)."""
    r = world()
    s = decide(mixes(r), r, 0, SwitchMix(OUTER))
    assert work(s, D).rate == 5000 and make(s, r, D, Z).per_hour == 500
    assert decide(s, r, 0, SaveMix(Mix(MixId("x2"), (CardShare(C, 4000), CardShare(D, 6000))))).mixes[-1].id == "x2"
