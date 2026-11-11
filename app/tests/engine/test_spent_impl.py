"""A share on a spent store yields (engine DESIGN.txt, "SPENT", invariants 133-141): the implementation's own tests of
the fixpoint and the yield's arithmetic, beside the blind contract suite."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, Amount, CardDef, CardId, CardShare, Flow, FlowKind, LaneDef, LaneId, Leave, Mix,
    MixId, Outcome, PacingCurve, RateRef, Rules, Run, RunKind, SaveMix, SkillDef, SkillId, SpentShare, StandingDef,
    StoreDef, StoreId, SwitchMix, TriggerDef, TriggerId, Unlock, UnlockKind, ActionId, advance, decide, explain,
    new_save, per_hour, view,
)
from ashfall_app.api import convert, models as w
from ashfall_app.engine.spent import spent_stores, yielded

A, B, C, P = (StoreId(n) for n in ("a", "b", "c", "p"))
M = MixId("m")


def rules(cards: tuple[CardDef, ...], stores: tuple[StoreDef, ...], standing: tuple[StandingDef, ...] = (),
          opening: tuple[Unlock, ...] | None = None) -> Rules:
    return Rules(stores, (SkillDef(SkillId("k")),), standing, PacingCurve((10**15,)), cards=cards,
                 lanes=(LaneDef(LaneId("la"), True),), opening=opening)


def empty(*ids: StoreId) -> tuple[StoreDef, ...]:
    return tuple(StoreDef(s, 100 * Q, 0) for s in ids)


def test_a_dry_cycle_with_nothing_feeding_it_is_spent_and_a_free_maker_breaks_it():
    cycle = (CardDef(CardId("ab"), 10, makes=(Flow(A, 1000),), costs=(Flow(B, 1000),)),
             CardDef(CardId("ba"), 10, makes=(Flow(B, 1000),), costs=(Flow(A, 1000),)))
    r = rules(cycle, empty(A, B))
    assert spent_stores(new_save(r), r) == {A, B}
    fed = rules(cycle + (CardDef(CardId("free"), 10, makes=(Flow(B, 1000),)),), empty(A, B))
    assert spent_stores(new_save(fed), fed) == frozenset()


def test_a_maker_whose_input_holds_something_keeps_its_store_out_and_a_drain_takes_nothing():
    r = rules((CardDef(CardId("ac"), 10, makes=(Flow(C, 1000),), costs=(Flow(A, 1000),)),),
              (StoreDef(A, 100 * Q, Q), *empty(C)))
    assert spent_stores(new_save(r), r) == {A}
    drained = rules((CardDef(CardId("ac"), 10, makes=(Flow(C, 1000),), drains=(Amount(A, Q),)),), empty(A, C))
    assert spent_stores(new_save(drained), drained) == {A}


def test_a_locked_maker_and_a_locked_standing_keep_nothing_out():
    maker = CardDef(CardId("mk"), 10, makes=(Flow(A, 1000),))
    stand = StandingDef(ActionId("st"), makes=(Flow(B, 1000),))
    r = rules((maker,), empty(A, B), (stand,), opening=())
    assert spent_stores(new_save(r), r) == {A, B}
    opened = rules((maker,), empty(A, B), (stand,),
                   opening=(Unlock(UnlockKind.CARD, maker.id), Unlock(UnlockKind.ACTION, stand.id)))
    assert spent_stores(new_save(opened), opened) == frozenset()


def _spent(card: str, share: int) -> tuple[CardId, int, Run]:
    return CardId(card), share, Run(RunKind.SPENT, 0, 1, P)


def _full(card: str, share: int) -> tuple[CardId, int, Run]:
    return CardId(card), share, Run(RunKind.FULL)


def test_the_yield_floors_once_per_pair_names_each_source_and_stays_on_its_lane():
    lanes = {"k1": "x", "k2": "x", "r1": "x", "r2": "x", "o": "y"}
    entries = (_spent("k1", 1000), _full("r1", 3000), _spent("k2", 999), _full("r2", 1000), _full("o", 2000))
    out, gains = yielded(entries, lambda c: LaneId(lanes[c]))
    assert gains == {CardId("r1"): (SpentShare(CardId("k1"), 750), SpentShare(CardId("k2"), 749)),
                     CardId("r2"): (SpentShare(CardId("k1"), 250), SpentShare(CardId("k2"), 249))}
    assert [share for _, share, _ in out] == [1000, 4499, 999, 1499, 2000]


def test_nothing_moves_when_the_rest_of_the_lane_has_no_share():
    entries = (_spent("k", 4000), _full("z", 0))
    assert yielded(entries, lambda _: LaneId("x")) == (entries, {})


def test_a_receiver_paused_after_the_yield_resumes_at_an_hour_of_its_saved_share():
    """The dry rule pauses by effective shares, but writes the resume level from the saved share (DESIGN.txt, "SPENT",
    QUESTIONS)."""
    cards = (CardDef(CardId("pool"), 10, costs=(Flow(P, per_hour(4)),)),
             CardDef(CardId("eat"), 10, costs=(Flow(A, per_hour(4)),)),
             CardDef(CardId("mk"), 10, makes=(Flow(A, per_hour(3)),)))
    r = rules(cards, (*empty(P), StoreDef(A, 100 * Q, 0)))
    mix = Mix(M, (CardShare(CardId("pool"), 5000), CardShare(CardId("eat"), 2500), CardShare(CardId("mk"), 2500)))
    s = decide(decide(new_save(r), r, 0, SaveMix(mix)), r, 0, SwitchMix(M))
    eat = next(p for p in s.pauses if p.runner == "eat")
    assert eat.resume_at == min(100 * Q, 3600 * (per_hour(4) * 2500 // BP))
    assert explain(s, r, RateRef(CardId("mk"), FlowKind.MAKE, A)).gained != ()
    assert [c.run for c in view(s, r).cards] == [RunKind.SPENT, RunKind.PAUSED, RunKind.FULL]


def test_the_wire_carries_the_saved_share_the_spent_store_and_each_gain():
    cards = (CardDef(CardId("pool"), 10, costs=(Flow(P, per_hour(4)),)), CardDef(CardId("rest"), 10))
    r = rules(cards, empty(P))
    mix = Mix(M, (CardShare(CardId("pool"), 6000), CardShare(CardId("rest"), 3000)))
    s = decide(decide(new_save(r), r, 0, SaveMix(mix)), r, 0, SwitchMix(M))
    wire = {c.card: c for c in convert.view(s, view(s, r)).cards}
    assert (wire["pool"].run, wire["pool"].spent_store, wire["pool"].share_bp) == (w.RunKind.SPENT, "p", 6000)
    assert (wire["rest"].share_bp, wire["rest"].gained) == (3000, [w.SpentShare(card="pool", share_bp=6000)])
    assert wire["rest"].spent_store is None and wire["pool"].gained == []


def test_a_standing_a_leave_stopped_is_no_maker_so_its_pool_is_spent_and_the_share_yields():
    """LEAVES, Stops: a stopped standing reads as locked everywhere, no maker (SPENT). The pool's only maker is the
    standing the lane's leave stops, so from the leave the pool is spent and the card eating it yields its share."""
    src = StandingDef(ActionId("src"), makes=(Flow(P, per_hour(1)),))
    cards = (CardDef(CardId("pool"), 10, costs=(Flow(P, per_hour(4)),)), CardDef(CardId("rest"), 10),
             CardDef(CardId("town"), 10, lane=LaneId("la")))
    leave = TriggerDef(TriggerId("leave"), AfterTime(10), Outcome(leaves=(Leave(LaneId("la"), (src.id,)),)))
    r = replace(rules(cards, empty(P), (src,)), triggers=(leave,))
    mix = Mix(M, (CardShare(CardId("pool"), 6000), CardShare(CardId("rest"), 3000)))
    s = decide(decide(new_save(r), r, 0, SaveMix(mix)), r, 0, SwitchMix(M))
    assert P not in spent_stores(advance(s, r, 5), r)
    after = advance(s, r, 50)
    assert P in spent_stores(after, r)
    assert [(c.card, c.run, c.gained) for c in view(after, r).cards if c.card != "town"] == [
        ("pool", RunKind.SPENT, ()), ("rest", RunKind.FULL, (SpentShare(CardId("pool"), 6000),))]
