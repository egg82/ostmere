"""CHOICES "Orders", the pot on the fire (decisions/mixes.md, "One pot on the fire"): the player's rules on a station lane
set which of its kinds is on, and nothing else does. The world is the pot's shape: one lane of uncapped cards, each
eating its own store."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, AfterTime, AtLeast, CardDef, CardId, Flow, LaneDef, LaneId, Order, PacingCurve, Rules,
    Save, SetOrders, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue, TapCard, advance, decide, new_save,
    per_hour,
)

POT = LaneId("pot")
SA, SB, SC = StoreId("sa"), StoreId("sb"), StoreId("sc")
PA, PB, PC = CardId("pa"), CardId("pb"), CardId("pc")
SK = SkillId("k0")
WORK_S = 60
ALWAYS = AfterTime(0)


def _rules(sa0: int, sb0: int, sc0: int = 0, sb_rate: int = 0) -> Rules:
    """Three kinds eating one a minute each. `sb_rate` items an hour reach SB from a standing action."""
    eat = Flow(SA, per_hour(1)), Flow(SB, per_hour(1)), Flow(SC, per_hour(1))
    cards = tuple(CardDef(c, WORK_S, lane=POT, costs=(f,)) for c, f in zip((PA, PB, PC), eat))
    standing = (StandingDef(ActionId("grow"), makes=(Flow(SB, per_hour(sb_rate)),)),) if sb_rate else ()
    return Rules(stores=(StoreDef(SA, 100 * Q, sa0 * Q), StoreDef(SB, 100 * Q, sb0 * Q), StoreDef(SC, 100 * Q, sc0 * Q)),
                 skills=(SkillDef(SK),), standing=standing, curve=PacingCurve((10**15,)), lanes=(LaneDef(POT),), cards=cards)


def _on(s: Save, r: Rules, t: int) -> CardId | None:
    s = advance(s, r, t)
    return next(ls.card for ls in s.lanes if ls.lane == POT)


def _set(r: Rules, *orders: Order) -> Save:
    return decide(new_save(r), r, 0, SetOrders(orders))


def test_a_rule_above_the_always_rule_puts_its_kind_on_when_it_holds():
    r = _rules(sa0=50, sb0=0, sb_rate=60)
    s = _set(r, Order(AtLeast(StoreValue(SB), 3 * Q, 3 * Q), TapCard(PB)), Order(ALWAYS, TapCard(PA)))
    assert _on(s, r, 1) == PA
    assert _on(s, r, 2 * WORK_S) == PA, "the rule's store is under its line, so the always rule's kind stays on"
    assert _on(s, r, 4 * WORK_S) == PB


def test_an_or_else_switches_when_the_chosen_kind_runs_out_and_the_game_makes_nothing():
    r = _rules(sa0=1, sb0=50, sc0=50)
    s = _set(r, Order(ALWAYS, TapCard(PA), or_else=(TapCard(PB), TapCard(PC))))
    assert _on(s, r, 10) == PA
    assert _on(s, r, 3 * WORK_S * 60) == PB


def test_with_no_rule_that_can_act_the_pot_goes_off_and_the_game_puts_no_kind_on():
    r = _rules(sa0=1, sb0=50)
    s = _set(r, Order(ALWAYS, TapCard(PA)))
    assert _on(s, r, 10) == PA
    assert _on(s, r, 3 * WORK_S * 60) is None, "the kind is out and nothing else is put on"
