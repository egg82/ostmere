"""Invariant 118, the wire half (api/CONTRACT.txt, "FIGHTS"; engine DESIGN.txt, "View"): Strength.sources carries each held
entry once, source the card's id and share_bp = h(c) with amount_bp what that share gives, and share_bp null on every
other entry, a permanent entry the same card's outcome landed included. Built on the real opening as
tests/test_fights_wire.py is, with the fight card gather_wood also holding 2500 on the hand."""
from dataclasses import replace
from functools import cache

import pytest

from ashfall_app import engine as e
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.opening.fight_entries import SideEntry, ThreatEntry
from ashfall_app.opening.schema import load_opening, to_rules
from ashfall_app.saves.ruleset import ruleset
from held_world import kills, wr

HAND, WOLF = e.SideId("hand"), e.ThreatId("wolf")
CARD = e.CardId("gather_wood")
PERMANENT = e.Modifier(e.SideStrength(HAND), e.ModifierKind.ADD_BP, 700, e.SourceId(CARD))
"""What the same card's own outcome may land for good: sourced by the bare card id."""
GEAR = e.Modifier(e.SideStrength(HAND), e.ModifierKind.MUL_BP, 2 * e.BP, e.SourceId("gear"))
HELD_BP = 2500


@cache
def rules() -> e.Rules:
    base = to_rules(load_opening())
    lost = e.StoreId("dry_wood")
    cards = tuple(replace(c, fight=e.FightDef(HAND, WOLF, lost), while_running=(wr(HAND, HELD_BP),)) if c.id == CARD else c
                  for c in base.cards)
    assert base.opening is not None
    opening = (*base.opening, e.Unlock(e.UnlockKind.CARD, CARD))
    return replace(base, cards=cards, opening=opening, sides=(*base.sides, e.SideDef(HAND, 300)),
                   threats=(*base.threats, e.ThreatDef(WOLF, 100)))


@cache
def game() -> Game:
    o = load_opening()
    o = o.model_copy(update={"sides": [*o.sides, SideEntry(id=HAND, label_key="side.hand", base=300)],
                             "threats": [*o.threats, ThreatEntry(id=WOLF, label_key="threat.wolf", base=100)]})
    return Game(o, replace(ruleset(o, [], "test", 1), rules=rules()))


@pytest.fixture(scope="module", autouse=True)
def built_world() -> None:
    """The rules and the game are cached; build them in setup so no test's timed call pays for loading the opening."""
    game()


def power(save: e.Save) -> w.Strength:
    fights = [f for f in game().view(save).fights if f.runner == CARD]
    assert len(fights) == 1
    return fights[0].power


def entry(source: str | None, form: w.StrengthKind, amount_bp: int, share_bp: int | None) -> w.StrengthEntry:
    return w.StrengthEntry(source=source, form=form, amount_bp=amount_bp, share_bp=share_bp)


@kills(14, 17, 18, 22)
def test_a_tap_serves_its_held_entry_with_the_card_id_and_a_whole_share_and_a_permanent_one_with_none():
    r = rules()
    s = e.decide(e.new_save(r, (PERMANENT, GEAR)), r, 0, game().verb(w.TapCard(card=CARD)))
    p = power(e.advance(s, r, 3))
    expected_sources = [
        entry(None, w.StrengthKind.BASE, 300, None),
        entry(CARD, w.StrengthKind.ADD_BP, 700, None),
        entry(CARD, w.StrengthKind.ADD_BP, HELD_BP, e.BP),
        entry("gear", w.StrengthKind.MUL_BP, 2 * e.BP, None)]
    assert p == w.Strength(value=300 * (e.BP + 700 + HELD_BP) * 2 * e.BP // e.BP ** 2, sources=expected_sources)


@kills(1, 14, 17, 18, 22)
def test_a_mix_share_serves_the_share_and_what_it_gives_and_every_other_entry_serves_null():
    r = rules()
    s = e.decide(e.new_save(r, (GEAR,)), r, 0, e.SaveMix(e.Mix(e.MixId("m"), (e.CardShare(CARD, 3000),))))
    s = e.decide(s, r, 0, e.SwitchMix(e.MixId("m")))
    p = power(e.advance(s, r, 3))
    assert [x for x in p.sources if x.share_bp is not None] == [
        entry(CARD, w.StrengthKind.ADD_BP, HELD_BP * 3000 // e.BP, 3000)]
    assert [x.share_bp for x in p.sources if x.source != CARD] == [None, None]
    wire = game().view(e.advance(s, r, 3))
    assert w.View.model_validate(wire.model_dump()) == wire
    threat = next(f.threat_strength for f in wire.fights if f.runner == CARD)
    assert all(x.share_bp is None for x in threat.sources)


@kills(4, 17)
def test_a_card_that_holds_nothing_serves_no_share_anywhere():
    r = rules()
    s = e.new_save(r, (PERMANENT,))
    p = power(e.advance(s, r, 3))
    assert [x.share_bp for x in p.sources] == [None, None] and [x.source for x in p.sources] == [None, CARD]
