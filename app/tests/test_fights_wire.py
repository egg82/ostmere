"""Fights on the wire (api/CONTRACT.txt, "FIGHTS"), on the real opening given one fight card and one standing fight:
the content's side, threat and fight infos, and the view's fights after a tap and an advance, each a plain copy of
the engine's FightView (the odds themselves are the engine's: tests/engine_contract/test_fight_view.py)."""
from dataclasses import replace
from functools import cache

import pytest

from ashfall_app import engine as e
from ashfall_app.api import content_models as cm
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.opening.fight_entries import SideEntry, ThreatEntry
from ashfall_app.opening.schema import load_opening, to_rules
from ashfall_app.saves.ruleset import ruleset

HAND, WOLF = e.SideId("hand"), e.ThreatId("wolf")
HUNT, RAID = e.CardId("gather_wood"), e.ActionId("chill")
Q = e.QUANTITY_SCALE
LOSES, WOUNDS = (e.Amount(e.StoreId("fullness"), 3 * Q),), (e.Amount(e.StoreId("nails"), 2 * Q),)
GEAR = e.Modifier(e.SideStrength(HAND), e.ModifierKind.MUL_BP, 2 * e.BP, e.SourceId("gear"))


@cache
def rules() -> e.Rules:
    base = to_rules(load_opening())
    lost, fought, raid_lost = (e.StoreId(s) for s in ("dry_wood", "damp_wood", "stones"))
    cards = tuple(replace(c, fight=e.FightDef(HAND, WOLF, lost, loses=LOSES, wounds=WOUNDS)) if c.id == HUNT else c
                  for c in base.cards)
    # the real chill costs warmth, which is dry at the start, so it would sit paused
    standing = tuple(replace(a, costs=(), fight=e.FightDef(HAND, WOLF, raid_lost, fought, e.per_hour(2), LOSES, WOUNDS))
                     if a.id == RAID else a for a in base.standing)
    assert base.opening is not None
    unlocked = (*base.opening, e.Unlock(e.UnlockKind.CARD, HUNT))
    return replace(base, cards=cards, standing=standing, opening=unlocked, sides=(*base.sides, e.SideDef(HAND, 300)), threats=(*base.threats, e.ThreatDef(WOLF, 100)))


def game_of(r: e.Rules) -> Game:
    o = load_opening()
    o = o.model_copy(update={"sides": [*o.sides, SideEntry(id=HAND, label_key="side.hand", base=300)],
                             "threats": [*o.threats, ThreatEntry(id=WOLF, label_key="threat.wolf", base=100)]})
    return Game(o, replace(ruleset(o, [], "test", 1), rules=r))


@cache
def game() -> Game:
    return game_of(rules())


@pytest.fixture(autouse=True, scope="module")
def primed() -> None:
    """Build the cached rules and game once for the module."""
    game()


def test_the_content_serves_the_sides_threats_and_each_runners_fight():
    c = game().content()
    assert [x for x in c.side_infos if x.side == "hand"] == [cm.SideInfo(side="hand", label_key="side.hand")]
    assert [x for x in c.threat_infos if x.threat == "wolf"] == [cm.ThreatInfo(threat="wolf", label_key="threat.wolf")]
    info = cm.FightInfo(side="hand", threat="wolf", loses=[cm.Amount(store="fullness", quantity=3 * Q)],
                        wounds=[cm.Amount(store="nails", quantity=2 * Q)], won_line_keys=[], lost_line_keys=[])
    assert [x.card for x in c.card_infos if x.fight == info] == ["gather_wood"]
    assert [x.action for x in c.standing_infos if x.fight == info] == ["chill"]
    shipped = to_rules(load_opening())   # control: nothing else carries one, beyond what the content ships
    real = sum(r.fight is not None for r in (*shipped.cards, *shipped.standing))
    assert sum(x.fight is not None for x in (*c.card_infos, *c.standing_infos)) == real + 2


def test_a_tap_and_an_advance_serve_the_fights_with_their_strengths_and_the_kept_odds():
    r = rules()
    s = e.decide(e.new_save(r, (GEAR,)), r, 0, game().verb(w.TapCard(card=HUNT)))
    wire = game().view(e.advance(s, r, 3600))
    assert w.View.model_validate(wire.model_dump()) == wire
    assert [(f.runner, f.side, f.threat) for f in wire.fights] == [("gather_wood", "hand", "wolf"), ("chill", "hand", "wolf")]
    f = wire.fights[0]
    assert f.power == w.Strength(value=600, sources=[
        w.StrengthEntry(source=None, form=w.StrengthKind.BASE, amount_bp=300, share_bp=None),
        w.StrengthEntry(source="gear", form=w.StrengthKind.MUL_BP, amount_bp=2 * e.BP, share_bp=None)])
    assert f.threat_strength == w.Strength(value=100, sources=[
        w.StrengthEntry(source=None, form=w.StrengthKind.BASE, amount_bp=100, share_bp=None)])
    assert f.loss_bp == -(-e.BP * 100 // (100 + 600)) and f.lost <= f.fought   # ceil(BP * T / (T + P))
    chill = wire.fights[1]
    assert 0 < chill.fought and chill.lost <= chill.fought   # control: the standing fight has run, so its tally is served


def test_a_held_entry_is_served_under_its_card_with_the_share_and_a_permanent_one_of_that_card_without():
    """CONTRACT.txt, "FIGHTS": source the bare card id and share_bp set for what the card holds while it runs; null on
    every other entry, so the page tells a card's held entry from a permanent one it landed."""
    r = rules()
    held = replace(r, cards=tuple(replace(c, while_running=(e.WhileRunning(HAND, 5000),)) if c.id == HUNT else c
                                  for c in r.cards))
    permanent = e.Modifier(e.SideStrength(HAND), e.ModifierKind.ADD_BP, 1000, e.SourceId(HUNT))
    s = e.decide(e.new_save(held, (permanent,)), held, 0, game().verb(w.TapCard(card=HUNT)))
    sources = game_of(held).view(s).fights[0].power.sources
    assert [(x.source, x.form, x.amount_bp, x.share_bp) for x in sources[1:]] == [
        (HUNT, w.StrengthKind.ADD_BP, 1000, None), (HUNT, w.StrengthKind.ADD_BP, 5000, e.BP)]
