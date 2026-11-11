"""Drains at 0, as built (engine DESIGN.txt, "DRAINS"): rebuild holds a store at 0 while its drains are forgiven
(lumps.forgiven), and the dry rule passes over the store's drains. The contract suite is in tests/engine_contract;
these pin the two mechanisms, each beside a control without the drain."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, Amount, CardDef, CardId, Flow, PacingCurve, Rules, Save, SkillDef, SkillId,
    StandingDef, StoreDef, StoreId, TapCard, advance, decide, new_save, per_hour, segment, validate_rules,
)
from ashfall_app.engine.segments import Segment

X, Y = StoreId("x"), StoreId("y")
C, HEAL = CardId("c"), ActionId("heal")


def world(x0: int, *, drain: int, heal: int = 0, inflow: int = 0) -> tuple[Rules, Save]:
    """Card c (an hour of work) draining `drain` of x a completion; a standing heal costing `heal` of x an hour, and a
    standing wound making `inflow` of x an hour."""
    standing = (StandingDef(HEAL, (Flow(Y, per_hour(1)),), (Flow(X, heal),)),) if heal else ()
    standing += (StandingDef(ActionId("wound"), (Flow(X, inflow),), ()),) if inflow else ()
    card = CardDef(C, 3600, drains=(Amount(X, drain),) if drain else ())
    r = Rules(stores=(StoreDef(X, 100 * Q, x0), StoreDef(Y, 100 * Q)), skills=(SkillDef(SkillId("k")),),
              standing=standing, curve=PacingCurve((10**15,)), cards=(card,))
    validate_rules(r)
    return r, new_save(r)


def test_a_drain_at_0_with_nothing_else_on_its_store_holds_it_still_and_its_tap_lands():
    r, s = world(Q // 2, drain=Q)
    s = decide(s, r, 0, TapCard(C))
    at_zero = advance(s, r, 1800)
    assert segment(at_zero, r, X) == Segment(1800, 0, 0)
    assert [ls.card for ls in at_zero.lanes] == [C] and at_zero.pauses == ()
    landed = advance(at_zero, r, 3600)
    assert [ls.card for ls in landed.lanes] == [None] and segment(landed, r, X).start_value == 0


def test_the_dry_rule_pauses_the_heal_and_never_the_drain():
    """x empties under the heal and the drain together; the heal is paused, the drain's tap runs on."""
    r, s = world(Q, drain=Q, heal=per_hour(1) // 2)
    s = advance(decide(s, r, 0, TapCard(C)), r, 2400)
    assert [p.runner for p in s.pauses] == [HEAL] and [ls.card for ls in s.lanes] == [C]
    assert segment(s, r, X) == Segment(2400, 0, 0)


def test_without_the_drain_the_heal_alone_is_paused_at_0():
    """The control: the same heal with no drain on x is paused when x empties, and nothing holds x still above it."""
    r, s = world(Q, drain=0, heal=per_hour(1))
    s = advance(s, r, 3600)
    assert [p.runner for p in s.pauses] == [HEAL] and segment(s, r, X) == Segment(3600, 0, 0)


def test_an_inflow_under_the_drain_leaves_x_at_0_and_one_over_it_lifts_x():
    weak = world(Q // 4, drain=Q, inflow=per_hour(1) // 2)
    s = advance(decide(weak[1], weak[0], 0, TapCard(C)), weak[0], 1800)
    assert segment(s, weak[0], X) == Segment(1800, 0, 0)
    strong = world(0, drain=Q, inflow=2 * per_hour(1))
    s = advance(decide(advance(strong[1], strong[0], 1), strong[0], 1, TapCard(C)), strong[0], 1801)
    assert segment(s, strong[0], X).start_value == 2000 + 1800 * (2000 - 1000)   # one second's inflow, then n - d
