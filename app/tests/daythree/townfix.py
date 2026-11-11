"""A fixture chapter with two joins for the town's mix (engine DESIGN.txt, "THE TOWN'S MIX"), until a real chapter has
them: two people, each with two uncapped cards making a store, each set to its first card by an always rule before
they join, and a trigger apiece that joins them to one town mix. `alt_rate` is the rate of each person's second card:
equal to the first's, the join's split is the best one; higher, a player re-splitting by hand beats it. Never a shipped
chapter (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import dataclass, field

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, CardDef, CardId, Flow, Join, LaneDef, LaneId, MixId, Order, Outcome, PacingCurve,
    Rules, Save, SetOrders, SkillDef, SkillId, StoreDef, StoreId, TapCard, TriggerDef, TriggerId, Verb, advance,
    decide, new_save, validate_rules,
)
from tests.daythree import town

H = 3600
WOOD, STONE = StoreId("wood"), StoreId("stone")
P1, P2 = LaneId("p1"), LaneId("p2")
P1_A, P1_B, P2_A, P2_B = CardId("p1_a"), CardId("p1_b"), CardId("p2_a"), CardId("p2_b")
TOWN = MixId("town:main")
SET = SetOrders((Order(AfterTime(0), TapCard(P1_A)), Order(AfterTime(0), TapCard(P2_A))))
"""The rules the player sets at the start: each person to their first card."""


def rules(alt_rate: int = Q, joins_at: tuple[int, int] = (H, 3 * H)) -> Rules:
    cards = (CardDef(P1_A, 100, lane=P1, makes=(Flow(WOOD, Q),)), CardDef(P1_B, 100, lane=P1, makes=(Flow(STONE, alt_rate),)),
             CardDef(P2_A, 100, lane=P2, makes=(Flow(STONE, Q),)), CardDef(P2_B, 100, lane=P2, makes=(Flow(WOOD, alt_rate),)))
    joins = tuple(TriggerDef(TriggerId(f"join_{lane}"), AfterTime(at), Outcome(joins=(Join(lane, TOWN),)))
                  for lane, at in zip((P1, P2), joins_at))
    r = Rules(stores=(StoreDef(WOOD, 10**9 * Q, 0), StoreDef(STONE, 10**9 * Q, 0)), skills=(SkillDef(SkillId("k")),),
              standing=(), curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(P1, True), LaneDef(P2, True)), cards=cards,
              triggers=joins)
    validate_rules(r)
    return r


@dataclass
class Played:
    save: Save
    log: list[tuple[int, Verb]] = field(default_factory=lambda: [])


def play(r: Rules, visits: tuple[int, ...], policy: town.Policy, until: int) -> Played:
    """From a new save: the player sets the people's rules at the first visit, then at each visit makes the policy's moves
    until it has none, and the rest is nobody deciding."""
    p = Played(new_save(r))
    for i, at in enumerate(visits):
        p.save = advance(p.save, r, at)
        if i == 0:
            _send(p, r, at, SET)
        while (m := policy(p.save, r)) is not None:
            for verb in m[1]:
                _send(p, r, at, verb)
    p.save = advance(p.save, r, until)
    return p


def _send(p: Played, r: Rules, at: int, verb: Verb) -> None:
    p.save = decide(p.save, r, at, verb)
    p.log.append((at, verb))
