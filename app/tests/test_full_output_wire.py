"""The wire's full_store (api/contract/full-output.txt, "FULL OUTPUT"): a card a full pause stopped is served paused with no blocker
and the store that has no room; a running card, a dry-paused one and the card once its pause lifts serve null."""
from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.engine import QUANTITY_SCALE as Q

P, Y = e.StoreId("p"), e.StoreId("y")
PULL, OTHER = e.CardId("pull"), e.CardId("other")
BIG = 10**6


def rules_of(*cards: e.CardDef, p0: int = BIG, y_cap: int = 4, standing: tuple[e.StandingDef, ...] = ()) -> e.Rules:
    stores = (e.StoreDef(P, BIG * Q, p0 * Q), e.StoreDef(Y, y_cap * Q, 0))
    r = e.Rules(stores, (e.SkillDef(e.SkillId("k")),), standing, e.PacingCurve((10**15,)), cards=cards)
    e.validate_rules(r)
    return r


def pull() -> e.CardDef:
    return e.CardDef(PULL, 10, inputs=(e.Amount(P, Q),), outcome=e.Outcome(stores=(e.Amount(Y, Q),)))


def mixed(rules: e.Rules) -> e.Save:
    s = e.decide(e.new_save(rules), rules, 0, e.SaveMix(e.Mix(e.MixId("m"), (e.CardShare(PULL, e.BP),))))
    return e.decide(s, rules, 0, e.SwitchMix(e.MixId("m")))


def _card(save: e.Save, rules: e.Rules, card: e.CardId) -> w.Card:
    wire = convert.view(save, e.view(save, rules))
    assert w.View.model_validate(wire.model_dump()) == wire
    return next(c for c in wire.cards if c.card == card)


def test_a_full_paused_card_serves_the_store_with_no_room():
    rules = rules_of(pull())
    s = mixed(rules)
    assert _card(e.advance(s, rules, 10), rules, PULL).full_store is None
    full = _card(e.advance(s, rules, 100), rules, PULL)
    assert (full.run, full.blocker, full.full_store) == (w.RunKind.PAUSED, None, "y")


def test_the_store_goes_once_the_pause_lifts():
    eat = e.StandingDef(e.ActionId("eat"), costs=(e.Flow(Y, e.per_hour(36)),))
    rules = rules_of(pull(), standing=(eat,))
    s = e.advance(mixed(rules), rules, 100)
    assert s.pauses and _card(s, rules, PULL).full_store == "y"
    while s.pauses:
        s = e.advance(s, rules, s.time + 10)
    assert _card(s, rules, PULL).full_store is None


def test_a_dry_paused_card_serves_null():
    """p holds two items and a card in play can refill it: pull runs p dry and pauses on it, a dry pause."""
    refill = e.CardDef(OTHER, 10, outcome=e.Outcome(stores=(e.Amount(P, Q),)))
    rules = rules_of(pull(), refill, p0=2, y_cap=BIG)
    dry = _card(e.advance(mixed(rules), rules, 1000), rules, PULL)
    assert dry.run == w.RunKind.PAUSED and dry.blocker is not None
    assert dry.full_store is None
