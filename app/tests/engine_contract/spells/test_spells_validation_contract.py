"""Validation of chains (engine/design/spells.txt, "SPELLS", "CHOICES (spells)": Validation; invariant 186), each refusal
paired with the valid control. Written blind from that part alone; messages are matched on the text the part gives."""
import re
from collections.abc import Callable
from typing import Any
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, ActionId, AfterTime, Amount, CardDef, CardId, ChainDef, FightDef, Flow, InvalidRulesError, Modifier, ModifierKind, Outcome,
    Rules, StandingDef, StoreDef, StoreId, ThreatDef, TriggerDef, TriggerId, per_hour, validate_rules, QUANTITY_SCALE as Q,
)
from spells_world import (
    BIG, CHAINED, FOUGHT, HAND, LINK_KEYS, PLAIN, RLOST, SPELL, WOLF, entry, kills, world,
)

type Edit = Callable[[Rules], Rules]
ADD, MUL = ModifierKind.ADD_BP, ModifierKind.MUL_BP
EXTRA, MORE, THIRD = StoreId("extra"), StoreId("more"), StoreId("third")


def threat(**kw: int) -> Edit:
    return lambda r: replace(r, threats=(ThreatDef(WOLF, 6, **kw),))


def chain(**kw: Any) -> Edit:
    def edit(r: Rules) -> Rules:
        c = r.cards[0].chain
        assert c is not None
        return replace(r, cards=(replace(r.cards[0], chain=replace(c, **kw)),))
    return edit


def with_stores(r: Rules) -> Rules:
    return replace(r, stores=(*r.stores, StoreDef(EXTRA, BIG), StoreDef(MORE, BIG), StoreDef(THIRD, BIG)))


def fight(**kw: Any) -> Edit:
    def edit(r: Rules) -> Rules:
        f = r.standing[0].fight
        assert f is not None
        return replace(r, standing=(replace(r.standing[0], fight=replace(f, **kw)),))
    return edit


def trig(*mods: Modifier) -> Edit:
    t = TriggerDef(TriggerId("t"), AfterTime(5), Outcome(modifiers=tuple(mods)))
    return lambda r: replace(r, triggers=(t,))


def plain(r: Rules) -> Rules:
    return replace(r, cards=(*r.cards, CardDef(PLAIN, 10)))


def card_fight(chained: StoreId | None, chain_too: bool) -> Edit:
    f = FightDef(HAND, WOLF, EXTRA, chained=chained)
    return lambda r: replace(with_stores(r), cards=(replace(r.cards[0], fight=f, chain=r.cards[0].chain if chain_too else None),))


def second_raid(chained: StoreId) -> Edit:
    two = StandingDef(ActionId("raid2"), fight=FightDef(HAND, WOLF, EXTRA, MORE, per_hour(1), chained=chained))
    return lambda r: replace(with_stores(r), standing=(*r.standing, two))


def calm_runner(r: Rules) -> Rules:
    return replace(r, standing=(*r.standing, StandingDef(ActionId("calm"))),
                   cards=(replace(r.cards[0], chain=ChainDef(ActionId("calm"), 2, LINK_KEYS[:1])),))


def outcome_makes(r: Rules) -> Rules:
    return replace(r, cards=(r.cards[0], CardDef(PLAIN, 10, outcome=Outcome(stores=(Amount(CHAINED, Q),)))))


def flow_makes(r: Rules) -> Rules:
    return replace(r, standing=(replace(r.standing[0], makes=(Flow(CHAINED, per_hour(1)),)),))


BAD: dict[str, tuple[Edit, str]] = {
    "members 0": (threat(members=0), "threat wolf: members must be >= 1"),
    "no standing action": (chain(runner=ActionId("nope")), "card spell: chain names nope, which is not a standing fight"),
    "a standing action with no fight": (calm_runner, "card spell: chain names calm, which is not a standing fight"),
    "no group": (threat(members=1), "card spell: chain names raid, whose threat wolf is not a group"),
    "no chained tally": (fight(chained=None), "card spell: chain names raid, which has no fought or chained tally"),
    "no fought tally": (fight(fought=None), "card spell: chain names raid, which has no fought or chained tally"),
    "reach 0": (chain(reach=0), "card spell: chain reach must be >= 1"),
    "no lines": (chain(lines=()), "card spell: a chain needs at least one line"),
    "a fight card with a chain": (card_fight(None, True), "card spell: a fight card has no chain"),
    "chained on a card's fight": (card_fight(THIRD, False), "chained belongs to a standing fight on a group threat"),
    "chained on a single creature": (lambda r: replace(threat(members=1)(r), cards=()),
                                     "chained belongs to a standing fight on a group threat"),
    "chained is fought": (fight(chained=FOUGHT), "chained tally store"),
    "chained is lost": (fight(chained=RLOST), "chained tally store"),
    "a flow makes chained": (flow_makes, "chained tally store"),
    "an outcome makes chained": (outcome_makes, "chained tally store"),
    "a trigger makes chained": (lambda r: replace(r, triggers=(TriggerDef(TriggerId("m"), AfterTime(5), Outcome(stores=(Amount(CHAINED, Q),))),)),
                                "chained tally store"),
    "another fight lists chained": (second_raid(CHAINED), "chained tally store"),
    "a falling add": (trig(entry(SPELL, ADD, -1)), "a chain's reach only rises"),
    "a falling mul": (trig(entry(SPELL, MUL, BP - 1)), "a chain's reach only rises"),
    "an unknown card": (trig(entry(CardId("zz"), ADD, 1)), "a modifier aims at an unknown id"),
    "a card with no chain": (lambda r: trig(entry(PLAIN, ADD, 1))(plain(r)), "a modifier aims at an unknown id"),
}


def refused(*names: str) -> None:
    for name in names:
        edit, message = BAD[name]
        with pytest.raises(InvalidRulesError, match=re.escape(message)):
            validate_rules(edit(world(3, 2)))


def test_the_valid_world_passes_the_controls():
    validate_rules(world(2, 2))
    validate_rules(world(3, 1))
    validate_rules(trig(entry(SPELL, ADD, 0), entry(SPELL, MUL, BP), entry(SPELL, ADD, 5000))(world(3, 2)))
    validate_rules(second_raid(THIRD)(world(3, 2)))
    validate_rules(card_fight(None, False)(world(3, 2)))


@kills(1)
def test_a_chain_on_a_threat_of_one_creature_is_refused_and_two_members_is_a_group():
    refused("no group")
    validate_rules(world(2, 2))


@kills(26)
def test_a_threat_of_no_members_is_refused():
    refused("members 0")


@kills(27)
def test_a_chain_names_a_standing_fight():
    refused("no standing action", "a standing action with no fight")


@kills(28)
def test_a_card_is_a_working_or_a_fight_never_both():
    refused("a fight card with a chain")


@kills(29)
def test_a_chain_has_a_reach_of_at_least_one_and_a_line():
    refused("reach 0", "no lines")
    validate_rules(chain(reach=1, lines=LINK_KEYS[:1])(world(3, 2)))


@kills(30)
def test_the_chained_tally_belongs_to_a_group_runner_and_is_required_where_a_chain_names_it():
    refused("no chained tally", "no fought tally", "chained on a card's fight", "chained on a single creature")


@kills(31)
def test_the_chained_tally_is_a_store_nothing_else_makes_or_counts():
    refused("chained is fought", "chained is lost", "a flow makes chained", "an outcome makes chained", "a trigger makes chained", "another fight lists chained")


@kills(32)
def test_a_reach_entry_only_raises_and_aims_at_a_card_with_a_chain():
    refused("a falling add", "a falling mul", "an unknown card", "a card with no chain")
