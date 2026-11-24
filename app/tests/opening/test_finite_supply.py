"""The finite-supply check (opening/finite_checks.py, issue #438): the shipped content passes, and each way a player could
soft-lock a finite store fails it, planted on the shipped rules or on small ones."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, AfterTime, AnswerDef, AnswerId, AtLeast, Amount, CardCount, CardDef, CardId, Flow,
    OfferDef, OfferId, Outcome, PacingCurve, Rules, SkillDef, SkillId, StandingDef, StoreDef, StoreId, TriggerDef,
    TriggerId, per_hour,
)
from ashfall_app.opening.convert import build_rules
from ashfall_app.opening.finite_checks import check_finite_supply
from ashfall_app.opening.schema import Opening

POOL, MADE, OTHER = StoreId("pool"), StoreId("made"), StoreId("other")
PULL, BUILD = CardId("pull"), CardId("build")


@pytest.fixture(scope="module")
def shipped_rules(shipped_opening: Opening) -> Rules:
    return build_rules(shipped_opening)


def test_the_shipped_content_passes(shipped_rules: Rules) -> None:
    check_finite_supply(shipped_rules)


def test_the_beams_store_back_at_eight_fails(shipped_rules: Rules) -> None:
    """The planted case of the issue: beams held 8 while the hall and the road take 12 of the ruin's 12."""
    stores = tuple(replace(d, cap=8 * Q) if d.id == StoreId("beams") else d for d in shipped_rules.stores)
    with pytest.raises(ValueError, match="store ruin_beams: .*into beams, whose cap is below"):
        check_finite_supply(replace(shipped_rules, stores=stores))


def _rules(*cards: CardDef, pool: int = 12, made_cap: int = 12, needed: int = 8, extra: tuple[TriggerDef, ...] = (),
           standing: tuple[StandingDef, ...] = (), offers: tuple[OfferDef, ...] = ()) -> Rules:
    """A pool filled once by a trigger, drawn into `made` by `pull` (1 for 1), and a project `build` taking one `made`
    a stage over `needed` stages, all of them read by a trigger."""
    build = CardDef(BUILD, 60, inputs=(Amount(MADE, Q),), cap=needed)
    stores = (StoreDef(POOL, 100 * Q), StoreDef(MADE, made_cap * Q), StoreDef(OTHER, 100 * Q))
    triggers = (TriggerDef(TriggerId("fill"), AfterTime(0), Outcome(stores=(Amount(POOL, pool * Q),))),
                TriggerDef(TriggerId("done"), AtLeast(CardCount(BUILD), needed, needed), Outcome()), *extra)
    return Rules(stores, (SkillDef(SkillId("k")),), standing, PacingCurve((10**15,)), cards=(build, *cards),
                 triggers=triggers, offers=offers)


def _pull(card: CardId = PULL, *outs: StoreId, cap: int | None = None) -> CardDef:
    return CardDef(card, 60, inputs=(Amount(POOL, Q),), outcome=Outcome(stores=tuple(Amount(s, Q) for s in outs or (MADE,))),
                   cap=cap)


def test_enough_with_a_cap_that_holds_it_all_passes() -> None:
    check_finite_supply(_rules(_pull()))


def test_a_pool_short_of_what_progress_needs_fails() -> None:
    with pytest.raises(ValueError, match="store (made|pool): finite"):
        check_finite_supply(_rules(_pull(), pool=7))


def test_an_answer_is_no_supply_since_it_may_be_declined() -> None:
    """The pool's last 4 come from an answer: counted, it would cover the 8; it is not."""
    offer = OfferDef(OfferId("o"), (AnswerDef(AnswerId("yes"), Outcome(stores=(Amount(POOL, 4 * Q),))), AnswerDef(AnswerId("no"))))
    check_finite_supply(_rules(_pull(), pool=8))
    with pytest.raises(ValueError, match="store (made|pool): finite"):
        check_finite_supply(_rules(_pull(), pool=4, offers=(offer,)))


def test_an_uncapped_optional_consumer_fails() -> None:
    other = CardDef(CardId("eat"), 60, inputs=(Amount(POOL, Q),), outcome=Outcome(stores=(Amount(OTHER, Q),)))
    with pytest.raises(ValueError, match="eat can spend it without limit"):
        check_finite_supply(_rules(_pull(), other))


def test_a_capped_optional_consumer_counts_its_whole_cap() -> None:
    """Pool 12, progress needs 8: a capped side job taking 4 fits, one taking 5 does not."""
    def side(cap: int) -> CardDef:
        return CardDef(CardId("side"), 60, inputs=(Amount(POOL, Q),), cap=cap)
    check_finite_supply(_rules(_pull(), side(4)))
    with pytest.raises(ValueError, match="store (made|pool): finite"):
        check_finite_supply(_rules(_pull(), side(5)))


def test_a_converter_into_a_store_smaller_than_progress_needs_fails() -> None:
    """made holds 4 of the 8 needed: a tap, or a by-product keeping the card running, would lose the pool at that cap."""
    with pytest.raises(ValueError, match="pull draws it into made, whose cap is below"):
        check_finite_supply(_rules(_pull(), made_cap=4, pool=13))


def test_a_standing_clock_drawing_a_pool_is_not_held_to_its_cap() -> None:
    clock = StandingDef(ActionId("clock"), costs=(Flow(POOL, per_hour(1)),), makes=(Flow(MADE, per_hour(1)),))
    check_finite_supply(_rules(standing=(clock,), made_cap=2))
