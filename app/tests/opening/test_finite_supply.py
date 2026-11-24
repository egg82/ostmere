"""The finite-supply check (opening/finite_checks.py, issue #438): the shipped content passes, and each way a player could
soft-lock a finite store fails it, planted on the shipped rules or on small ones."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, AfterTime, AnswerDef, AnswerId, AtLeast, Amount, CardCount, CardDef, CardId, Flow,
    OfferDef, OfferId, Outcome, PacingCurve, Rules, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue, TriggerDef,
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


@pytest.fixture(scope="module")
def tallies(shipped_opening: Opening) -> frozenset[StoreId]:
    return frozenset(StoreId(s.id) for s in shipped_opening.stores if s.tally)


def test_the_shipped_content_passes(shipped_rules: Rules, tallies: frozenset[StoreId]) -> None:
    check_finite_supply(shipped_rules, tallies)


def test_the_beams_store_back_at_eight_fails(shipped_rules: Rules, tallies: frozenset[StoreId]) -> None:
    """The planted case of the issue: beams held 8 while the hall and the road take 12 of the ruin's 12."""
    stores = tuple(replace(d, cap=8 * Q) if d.id == StoreId("beams") else d for d in shipped_rules.stores)
    with pytest.raises(ValueError, match="store ruin_beams: .*into beams, whose cap is below"):
        check_finite_supply(replace(shipped_rules, stores=stores), tallies)


def _reads_card(rules: Rules, trigger: str, card: str, n: int) -> Rules:
    """The shipped rules with `trigger` reading `card`'s count again, as before its tally."""
    when = AtLeast(CardCount(CardId(card)), n, n)
    return replace(rules, triggers=tuple(replace(t, when=when) if str(t.id) == trigger else t for t in rules.triggers))


def _no_walk_fungus(rules: Rules) -> Rules:
    """The shipped rules with fungus a season's pool again: the ashwood walk and its twin keep their other finds."""
    def dry(c: CardDef) -> CardDef:
        outcome = replace(c.outcome, stores=tuple(a for a in c.outcome.stores if a.store != StoreId("fungus")))
        return replace(c, outcome=outcome)
    return replace(rules, cards=tuple(dry(c) if str(c.id).endswith("walk_ashwood") else c for c in rules.cards))


def test_the_first_fungus_stew_read_off_the_hands_card_alone_fails(shipped_rules: Rules, tallies: frozenset[StoreId]) -> None:
    with pytest.raises(ValueError, match="store fungus: .*n\\d+_fungus_stew can spend it without limit"):
        check_finite_supply(_reads_card(_no_walk_fungus(shipped_rules), "t_caps", "fungus_stew", 1), tallies)


def test_the_fifth_cover_read_off_the_hands_card_alone_fails(shipped_rules: Rules, tallies: frozenset[StoreId]) -> None:
    with pytest.raises(ValueError, match="store rime: .*n\\d+_cover_beds can spend it without limit"):
        check_finite_supply(_reads_card(shipped_rules, "t_torn_clock", "cover_beds", 5), tallies)


def test_a_warming_that_does_not_count_toward_the_cover_tally_fails(shipped_rules: Rules, tallies: frozenset[StoreId]) -> None:
    """warm_beds spends the season's rime too, so it must add to the tally the fifth-cover trigger reads."""
    def uncounted(c: CardDef) -> CardDef:
        outcome = replace(c.outcome, stores=tuple(a for a in c.outcome.stores if a.store != StoreId("beds_covered")))
        return replace(c, outcome=outcome)
    cards = tuple(uncounted(c) if str(c.id) == "warm_beds" else c for c in shipped_rules.cards)
    with pytest.raises(ValueError, match="store rime: .*warm_beds can spend it without limit"):
        check_finite_supply(replace(shipped_rules, cards=cards), tallies)


def _rules(*cards: CardDef, pool: int = 12, made_cap: int = 12, needed: int = 8, extra: tuple[TriggerDef, ...] = (),
           standing: tuple[StandingDef, ...] = (), offers: tuple[OfferDef, ...] = (), build_cap: int | None = None) -> Rules:
    """A pool filled once by a trigger, drawn into `made` by `pull` (1 for 1), and a project `build` taking one `made`
    a stage over `needed` stages, all of them read by a trigger."""
    build = CardDef(BUILD, 60, inputs=(Amount(MADE, Q),), cap=build_cap or needed)
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



def test_a_required_cards_own_later_completions_spend_too_late_to_matter() -> None:
    """build may run 12 stages and progress reads 8: its last 4 come after its 8, so a pool of 8 is enough. A second
    project reading all 4 of its stages could be starved by them, so with it the pool needs 16."""
    check_finite_supply(_rules(_pull(), pool=8, build_cap=12))
    other = CardDef(CardId("build2"), 60, inputs=(Amount(MADE, Q),), cap=4)
    read = (TriggerDef(TriggerId("b2"), AtLeast(CardCount(CardId("build2")), 4, 4), Outcome()),)
    with pytest.raises(ValueError, match="store (made|pool): finite"):
        check_finite_supply(_rules(_pull(), other, pool=15, build_cap=12, extra=read))
    check_finite_supply(_rules(_pull(), other, pool=16, build_cap=12, extra=read))


def test_a_consumer_stopping_on_another_pool_spends_only_what_that_pool_lets_it() -> None:
    """A standing chore eats 1 of the pool an hour while its own clock (2 hours) lasts: it can spend 2, so a pool of 10
    covers the 8 and a pool of 9 does not."""
    clock = StoreId("other")
    eat = StandingDef(ActionId("eat"), costs=(Flow(POOL, per_hour(1)), Flow(clock, per_hour(1))))
    fill = (TriggerDef(TriggerId("clock"), AfterTime(0), Outcome(stores=(Amount(clock, 2 * Q),))),)
    check_finite_supply(_rules(_pull(), pool=10, standing=(eat,), extra=fill))
    with pytest.raises(ValueError, match="store (made|pool): finite"):
        check_finite_supply(_rules(_pull(), pool=9, standing=(eat,), extra=fill))


# A trigger reading an uncapped card's count (issue #438's follow-up): the count is a need like a project's, so a pool
# the card's town twins also draw fails while the trigger counts the card alone; a tally every copy adds to passes.
FUNGUS, TALLY = StoreId("fungus"), StoreId("tally")
STEW, TWIN = CardId("stew"), CardId("n1_stew")


def _copies(pool: int, take: int, read: int, tally: bool, *more: TriggerDef) -> Rules:
    """A pool of `pool` items no maker refills, drawn `take` a completion by an uncapped card and its twin; a trigger
    reads `read` of the card's count, or of a tally both add to."""
    out = Outcome(stores=(Amount(TALLY, Q),)) if tally else Outcome()
    cards = tuple(CardDef(c, 60, inputs=(Amount(FUNGUS, take * Q),), outcome=out) for c in (STEW, TWIN))
    when = AtLeast(StoreValue(TALLY), read * Q, read * Q) if tally else AtLeast(CardCount(STEW), read, read)
    stores = (StoreDef(FUNGUS, 1000 * Q, pool * Q), StoreDef(TALLY, read * Q))
    return Rules(stores, (SkillDef(SkillId("k")),), (), PacingCurve((10**15,)), cards=cards,
                 triggers=(TriggerDef(TriggerId("first"), when, Outcome()), *more))


def test_a_first_completion_read_while_a_twin_draws_the_same_pool_fails() -> None:
    """The first stew: one completion is all progress reads, but the twin can spend the whole pool before it."""
    with pytest.raises(ValueError, match="store fungus: finite and needed by progress, but n1_stew can spend it"):
        check_finite_supply(_copies(600, 6, 1, tally=False))


def test_a_fifth_completion_read_on_either_of_two_cards_fails() -> None:
    """The fifth cover by either hand: each trigger counts one card, and the other's covers spend the pool past it."""
    other = TriggerDef(TriggerId("either"), AtLeast(CardCount(TWIN), 5, 5), Outcome())
    with pytest.raises(ValueError, match="store fungus: finite and needed by progress, but .* can spend it without limit"):
        check_finite_supply(_copies(170, 12, 5, False, other))


def test_a_tally_every_copy_adds_to_passes() -> None:
    check_finite_supply(_copies(600, 6, 1, tally=True), frozenset({TALLY}))
    check_finite_supply(_copies(170, 12, 5, tally=True), frozenset({TALLY}))


def test_a_tally_the_pool_cannot_fill_fails() -> None:
    with pytest.raises(ValueError, match="store (fungus|tally): finite"):
        check_finite_supply(_copies(48, 12, 5, tally=True), frozenset({TALLY}))


def test_an_uncapped_cards_own_later_completions_spend_after_its_count() -> None:
    """With no twin and nothing else needing the pool, the card's completions past its count harm nothing."""
    rules = _copies(600, 6, 1, tally=False)
    check_finite_supply(replace(rules, cards=rules.cards[:1]))
