"""One order covers every stage of a staged build (DESIGN.txt, "ORDER CARD ON A STAGED BUILD"): an at_least order on the
store the build takes taps each stage as the store allows, is passed over at the build's cap, and the player's own mix
runs on throughout; a cure or a glowing step cuts in on a stage and the order taps the build again afterwards."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, AtLeast, AtMost, CardDef, CardId, CardShare, ChipDef, ChipId, Flow,
    Mix, MixId, Order, OrderState, Outcome, PacingCurve, Rules, Save, SaveMix, SetOrders, SkillDef, SkillId,
    StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, advance, decide, new_save, validate_rules, view,
)
from ashfall_app.engine import counts
from ashfall_app.engine.ids import ActionId

WOOD, FOOD = StoreId("wood"), StoreId("food")
CHOP, BUILD, EAT, STEP = CardId("chop"), CardId("build"), CardId("eat"), CardId("step")
HUNGRY = AtMost(StoreValue(FOOD), 5 * Q, 8 * Q)
COVERS = Order(AtLeast(StoreValue(WOOD), 2 * Q, Q), TapCard(BUILD))


def world(chip: bool = False, glows: bool = False) -> Rules:
    """CHOP (the player's mix) makes wood; each of BUILD's three 100 s stages takes 2 wood. With `chip`, FOOD drains
    to the chip's line while a stage runs, and EAT cures it."""
    fed = Outcome(stores=(Amount(FOOD, 5 * Q),))
    r = Rules(
        stores=(StoreDef(WOOD, 100 * Q, 0), StoreDef(FOOD, 100 * Q, 10 * Q)), skills=(SkillDef(SkillId("k")),),
        standing=(StandingDef(ActionId("body"), costs=(Flow(FOOD, 180_000),)),) if chip else (),
        curve=PacingCurve((10**9 * Q,)),
        cards=(CardDef(CHOP, 10, outcome=Outcome(stores=(Amount(WOOD, Q),))),
               CardDef(BUILD, 100, cap=3, inputs=(Amount(WOOD, 2 * Q),)), CardDef(EAT, 10, outcome=fed),
               CardDef(STEP, 5, cap=1, glows=glows)),
        chips=(ChipDef(ChipId("hungry"), HUNGRY),) if chip else ())
    validate_rules(r)
    return r


def played(r: Rules) -> Save:
    """The player's own mix (CHOP) running, and the one order covering BUILD."""
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m"), (CardShare(CHOP, BP),))))
    return decide(decide(s, r, 0, SwitchMix(MixId("m"))), r, 0, SetOrders((COVERS,)))


def mix_runs_on(s: Save, r: Rules) -> bool:
    v = view(s, r)
    return v.running_mix == MixId("m") and v.greyed_mixes == ()


def count(s: Save, r: Rules, card: CardId) -> int:
    return next(c.completions for c in view(s, r).cards + view(s, r).completed if c.card == card)


def work(s: Save, card: CardId) -> int:
    return next(cs.work.start_value for cs in s.cards if cs.card == card)


def test_one_order_lands_every_stage_and_the_players_mix_runs_on():
    r = world()
    s = played(r)
    for t in range(0, 4000, 50):
        s = advance(s, r, t)
    v = view(s, r)
    assert count(s, r, BUILD) == 3 and BUILD in [c.card for c in v.completed]
    assert mix_runs_on(s, r) and s.lanes[0].card is None
    assert v.order_states == (OrderState.PASSED_OVER,), "the order is passed over at the build's cap, and says so"
    assert count(s, r, CHOP) > 0 and advance(s, r, 8000).latches == s.latches


def test_the_order_holds_until_the_store_allows_the_next_stage():
    r = world()
    s = played(r)
    stages: list[tuple[int, int]] = []
    for t in range(0, 2000, 10):
        s = advance(s, r, t)
        if not stages or count(s, r, BUILD) != stages[-1][1]:
            stages.append((t, count(s, r, BUILD)))
    assert [n for _, n in stages] == [0, 1, 2, 3]


def test_a_planted_engine_that_greys_the_players_mix_at_the_cap_goes_red(monkeypatch: pytest.MonkeyPatch):
    r = world()
    real = counts.greyed

    def greys_the_players_mix(save: Save, rules: Rules, mix: MixId) -> bool:
        return real(save, rules, mix) or mix == MixId("m")

    monkeypatch.setattr(counts, "greyed", greys_the_players_mix)
    s = played(r)
    for t in range(0, 4000, 50):
        s = advance(s, r, t)
    assert not mix_runs_on(s, r), "the check the first test makes sees a greyed mix"


def test_a_cure_cuts_in_on_a_stage_and_the_order_taps_the_build_again():
    r = world(chip=True)
    s = played(r)
    s = advance(s, r, 100)
    assert s.lanes[0].card == BUILD and s.chips == (True,) and work(s, BUILD) > 0
    kept = work(s, BUILD)
    assert next(c.cuts_in for c in view(s, r).cards if c.card == EAT)
    s = decide(s, r, 100, TapCard(EAT))
    assert s.lanes[0].card == EAT and work(s, BUILD) == kept
    assert [e.verb for e in s.queue] == [TapCard(BUILD)], "the stage drank the wood that made the order true, so the queue holds it"
    for t in range(110, 5000, 50):
        s = advance(s, r, t)
    assert s.queue == () and count(s, r, BUILD) == 3, "the stage finished from its kept work, then the order landed the rest"


def test_a_glowing_step_cuts_in_on_a_stage_and_the_order_taps_the_build_again():
    r = world(glows=True)
    s = advance(played(r), r, 100)
    assert s.lanes[0].card == BUILD and next(c.cuts_in for c in view(s, r).cards if c.card == STEP)
    kept = work(s, BUILD)
    s = advance(decide(s, r, 100, TapCard(STEP)), r, 105)
    assert s.lanes[0].card == BUILD and work(s, BUILD) >= kept
    for t in range(110, 5000, 50):
        s = advance(s, r, t)
    assert count(s, r, BUILD) == 3
