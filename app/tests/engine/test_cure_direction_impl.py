"""DESIGN.txt, "CURE CUT-IN": a card cures a chip when it moves the chip's store toward clearing it, by the chip's own
condition: up for a chip that shows while the store is low (AtMost), down for one that shows while it is high (AtLeast)."""
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, AtLeast, AtMost, CardDef, CardId, ChipDef, ChipId, Flow, Outcome, PacingCurve,
    Rules, Save, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue, TapCard, advance, decide, new_save,
    validate_rules, view,
)
from ashfall_app.engine.cure_reading import cures_chip, cures_shown
from ashfall_app.engine.ids import ActionId

BUILD, CLEAR, DUMP = CardId("build"), CardId("clear"), CardId("dump")
ASH = StoreId("ash")
LAID = ChipId("laid")


def world(ash: int = 0, chip: AtLeast | AtMost = AtLeast(StoreValue(ASH), 5 * Q, 3 * Q)) -> Rules:
    """ASH builds up fast enough that the chip shows at 100 s while a 1000 s stage runs. CLEAR
    takes 5 items of it (an input); DUMP adds 5 (it makes the chip worse)."""
    r = Rules(stores=(StoreDef(ASH, 100 * Q, ash),), skills=(SkillDef(SkillId("k")),),
              standing=(StandingDef(ActionId("fall"), makes=(Flow(ASH, 180_000),)),), curve=PacingCurve((10**9 * Q,)),
              cards=(CardDef(BUILD, 1000, cap=3), CardDef(CLEAR, 10, inputs=(Amount(ASH, 5 * Q),)),
                     CardDef(DUMP, 10, outcome=Outcome(stores=(Amount(ASH, 5 * Q),)))),
              chips=(ChipDef(LAID, chip),))
    validate_rules(r)
    return r


def building(r: Rules, t: int) -> Save:
    return advance(decide(new_save(r), r, 0, TapCard(BUILD)), r, t)


def cuts_in(r: Rules, s: Save, card: CardId) -> bool:
    return next(c.cuts_in for c in view(s, r).cards if c.card == card)


def test_a_take_cures_a_high_chip_and_cuts_in_while_it_shows():
    r = world()
    s = building(r, 100)
    assert s.chips == (True,) and cures_shown(s, r, CLEAR) and cuts_in(r, s, CLEAR)
    s = decide(s, r, 100, TapCard(CLEAR))
    assert s.lanes[0].card == CLEAR
    assert next(c.work.start_value for c in s.cards if c.card == BUILD) == 100 * BP, "the build's work was kept"


def test_a_take_does_not_cut_in_while_the_chip_does_not_show():
    r = world()
    s = building(r, 10)
    assert s.chips == (False,) and not cures_shown(s, r, CLEAR) and not cuts_in(r, s, CLEAR)


def test_an_add_does_not_cure_a_high_chip():
    r = world()
    s = building(r, 100)
    assert s.chips == (True,) and not cures_shown(s, r, DUMP) and not cuts_in(r, s, DUMP)
    assert cures_chip(r, CLEAR, LAID) and not cures_chip(r, DUMP, LAID)


def test_a_take_does_not_cure_a_low_chip():
    r = world(chip=AtMost(StoreValue(ASH), 5 * Q, 8 * Q))
    assert cures_chip(r, DUMP, LAID) and not cures_chip(r, CLEAR, LAID)
