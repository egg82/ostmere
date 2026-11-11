"""The cures gate (cures.py) on fixture rules, for a chip on a count store that a capped build's completion-count
trigger adds to: the build's stages cure it, and each way the stages cannot reach the chip fails."""
from ashfall_app.engine import (
    Amount, AtLeast, AtMost, CardCount, CardDef, CardId, ChipDef, ChipId, Outcome, PacingCurve, Rules, SkillDef, SkillId,
    StoreDef, StoreId, StoreValue, TriggerDef, TriggerId, Unlock, UnlockKind, new_save, view,
)
from ashfall_app.engine.cure_reading import puts_up
from tests.dayone import cures

COUNT, OTHER, WOOD = StoreId("count"), StoreId("other"), StoreId("wood")
BUILD, GATHER, COLD = CardId("build"), CardId("gather"), ChipId("cold")
Q = 3600
BUILD_S = 400


def world(count: int = 2, cap: int | None = 3, adds: StoreId = COUNT, build_s: int = BUILD_S, gather_s: int | None = None,
          shown_to: int = 0, later: int | None = None) -> Rules:
    """A chip shown while `count` is empty; BUILD (capped at `cap`, `build_s` long) with a trigger adding `adds` at its
    `count`th completion (and one more of COUNT at its `later`th); the chip is shown while COUNT is at most `shown_to` quanta;
    with `gather_s`, BUILD needs wood and only a GATHER of that length makes it."""
    need = Amount(WOOD, Q)
    build = CardDef(BUILD, build_s, cap=cap, requires=(AtLeast(StoreValue(WOOD), need.quantity, need.quantity),)
                    if gather_s else ())
    cards = (build,) if gather_s is None else (build, CardDef(GATHER, gather_s, outcome=Outcome(stores=(need,))))
    triggers = (TriggerDef(TriggerId("t"), AtLeast(CardCount(BUILD), count, count), Outcome(stores=(Amount(adds, Q),))),
                *(TriggerDef(TriggerId("u"), AtLeast(CardCount(BUILD), n, n), Outcome(stores=(Amount(COUNT, Q),)))
                  for n in (later,) if n is not None))
    unlocked = (Unlock(UnlockKind.CHIP, COLD), *(Unlock(UnlockKind.CARD, c.id) for c in cards))
    return Rules((StoreDef(COUNT, 10 * Q), StoreDef(OTHER, 10 * Q), StoreDef(WOOD, 10 * Q)), (SkillDef(SkillId("k")),), (),
                 PacingCurve((10**15,)), cards=cards, triggers=triggers, opening=unlocked,
                 chips=(ChipDef(COLD, AtMost(StoreValue(COUNT), shown_to * Q, shown_to * Q)),))


def cured(rules: Rules) -> bool:
    save = new_save(rules)
    v = view(save, rules)
    assert COLD in v.chips, "the chip must show for the check to mean anything"
    return cures.cured(save, rules, v, COLD)


def test_a_chip_on_a_count_store_a_builds_count_trigger_adds_to_is_cured():
    assert cured(world())


def test_the_reading_names_the_count_trigger_store_for_the_card():
    assert puts_up(world(), world().cards[0]) == {"count"}
    assert puts_up(world(adds=OTHER), world().cards[0]) == {"other"}


def test_a_trigger_adding_another_store_does_not_cure_the_chip():
    assert not cured(world(adds=OTHER))


def test_a_count_past_the_cap_does_not_cure_the_chip():
    assert cured(world(count=4, cap=5))
    assert not cured(world(count=4, cap=3))


def test_a_build_that_cannot_start_within_the_window_does_not_cure_the_chip():
    assert cured(world(gather_s=60))
    assert not cured(world(gather_s=cures.CURE_S + 60))


def test_a_card_without_a_cap_keeps_the_window():
    assert cured(world(count=2, cap=None, build_s=cures.CURE_S // 2 - 1))
    assert not cured(world(count=2, cap=None))


def test_a_chip_still_shown_when_the_counted_completion_lands_is_not_cured_by_a_later_one():
    assert cured(world(count=2, shown_to=1, later=None)) is False
    assert not cured(world(count=2, shown_to=1, later=3))
    assert cured(world(count=2, shown_to=0, later=3))
