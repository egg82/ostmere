"""A chain on the wire (api/contract/spells.txt, "SPELLS"; engine/design/spells.txt for the numbers behind it), written
blind from those parts alone, on the real opening given one standing fight on a group threat and one working that chains
it: the content's group size and chain, View.chains and Fight.chained as plain copies of the engine's reads, and a link
told as a line of its own."""
from dataclasses import replace
from functools import cache

import pytest

from ashfall_app import engine as e
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.opening.chain_entries import ChainEntry
from ashfall_app.opening.fight_entries import SideEntry, ThreatEntry
from ashfall_app.opening.schema import Opening, load_opening, to_rules
from ashfall_app.saves.interface import Played
from ashfall_app.saves.ruleset import ruleset
from spells_world import kills

HAND, WOLF = e.SideId("hand"), e.ThreatId("wolf")
WORKING, RAID = e.CardId("gather_wood"), e.ActionId("chill")
LOST, FOUGHT, CHAINED = (e.StoreId(s) for s in ("spell_lost", "spell_fought", "spell_chained"))
KEYS = ("spell.link.a", "spell.link.b")
MEMBERS, REACH = 50, 3
BIG = 10**6 * e.QUANTITY_SCALE
PAY = e.Modifier(e.ChainReach(WORKING), e.ModifierKind.ADD_BP, 10_000, e.SourceId("pay"))


@cache
def shipped() -> Opening:
    return load_opening()


@cache
def rules() -> e.Rules:
    base = to_rules(shipped())
    cards = tuple(replace(c, chain=e.ChainDef(RAID, REACH, tuple(e.LineKey(k) for k in KEYS))) if c.id == WORKING else c
                  for c in base.cards)
    fight = e.FightDef(HAND, WOLF, LOST, FOUGHT, e.per_hour(3600), chained=CHAINED)
    standing = tuple(replace(a, costs=(), fight=fight) if a.id == RAID else a for a in base.standing)
    assert base.opening is not None
    stores = (*base.stores, *(e.StoreDef(s, BIG) for s in (LOST, FOUGHT, CHAINED)))
    return replace(base, cards=cards, standing=standing, stores=stores, opening=(*base.opening, e.Unlock(e.UnlockKind.CARD, WORKING)),
                   sides=(*base.sides, e.SideDef(HAND, 300)), threats=(*base.threats, e.ThreatDef(WOLF, 100, members=MEMBERS)))


@cache
def game() -> Game:
    chain = ChainEntry(runner=RAID, reach=REACH, link_line_keys=list(KEYS))
    o = shipped().model_copy(update={"sides": [*shipped().sides, SideEntry(id=HAND, label_key="side.hand", base=300)],
                                     "threats": [*shipped().threats, ThreatEntry(id=WOLF, label_key="threat.wolf", base=100, members=MEMBERS)],
                                     "cards": [c.model_copy(update={"chain": chain}) if c.id == WORKING else c for c in shipped().cards]})
    return Game(o, replace(ruleset(shipped(), "test", 1), rules=rules()))


@pytest.fixture(autouse=True, scope="module")
def primed() -> None:
    game()


def work_s() -> int:
    return next(c.work_s for c in rules().cards if c.id == WORKING)


def tapped(*mods: e.Modifier) -> e.Step:
    r = rules()
    s = e.decide(e.new_save(r, mods), r, 0, e.TapCard(WORKING))
    return e.advance_logged(s, r, work_s())


@kills(38)
def test_the_content_serves_the_group_size_and_the_chain_of_the_working():
    c = game().content()
    assert [x.members for x in c.threat_infos if x.threat == "wolf"] == [MEMBERS]
    assert {x.members for x in c.threat_infos if x.threat != "wolf"} == {1}
    chain = [x.chain for x in c.card_infos if x.card == "gather_wood"]
    assert chain[0] is not None and (chain[0].runner, chain[0].link_line_keys) == ("chill", list(KEYS))
    assert [x.card for x in c.card_infos if x.chain is not None] == ["gather_wood"]


@kills(39)
def test_view_chains_serve_the_reach_now_with_its_base_first_and_the_pay_after():
    r = rules()
    s = e.new_save(r, (PAY,))
    wire = game().view(s)
    assert [(c.card, c.runner) for c in wire.chains] == [("gather_wood", "chill")]
    up = wire.chains[0].up_to
    assert up.value == REACH * 2 == 6
    assert (up.sources[0].source, up.sources[0].form, up.sources[0].amount_bp) == (None, w.StrengthKind.BASE, REACH)
    assert [(x.source, x.form, x.amount_bp) for x in up.sources[1:]] == [("pay", w.StrengthKind.ADD_BP, 10_000)]
    assert w.View.model_validate(wire.model_dump()) == wire


@kills(40)
def test_a_fights_chained_is_the_whole_links_and_a_link_is_in_neither_fought_nor_lost():
    step = tapped()
    wire = game().view(step.save)
    chill = next(f for f in wire.fights if f.runner == "chill")
    k = min(MEMBERS - work_s() % MEMBERS, REACH)
    assert chill.chained == k > 1 and chill.chained == e.view(step.save, rules()).fights[-1].chained
    assert chill.fought == work_s() and chill.lost <= chill.fought


@kills(41)
def test_each_link_is_a_log_line_of_its_own_with_the_working_as_its_card():
    step = tapped()
    wire = game().step(Played(1, 1, step.save, step.lines))
    links = [x for x in wire.lines if x.card == "gather_wood" and x.key in KEYS]
    assert len(links) == min(MEMBERS - work_s() % MEMBERS, REACH) > 1
    assert [x.key for x in links] == [KEYS[min(i, 2) - 1] for i in range(1, len(links) + 1)]
    assert len({(x.at, x.seq) for x in links}) == len(links)
