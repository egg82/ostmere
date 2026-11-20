"""Invariant 183 (engine DESIGN.txt, "GROUPS (pooled lanes)", "Validation"): InvalidRulesError for each listed rule, one
message per rule, and none for valid rules."""
import re
from typing import Any
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerDef, AnswerId, CardDef, CardId, Flow, InvalidRulesError, Join, LaneDef, LaneId, Leave, Mark,
    OfferDef, OfferId, Outcome, RuleInstall, SkillId, TriggerDef, TriggerId, validate_rules,
)
from tests.kills import kills
from groups_world import (
    G, GA, P1, P2, PER_SECOND, Q1, TOWN, WORK, X, cards, join, lanes, mark, off, own, world,
)

G2 = LaneId("g2")


def refused(message: str, **changes: Any) -> None:
    r = world(check=False, **changes)
    with pytest.raises(InvalidRulesError, match=re.escape(message)):
        validate_rules(r)


def lanes_with(*changed: LaneDef) -> tuple[LaneDef, ...]:
    by_id = {ld.id: ld for ld in changed}
    return tuple(by_id.get(ld.id, ld) for ld in lanes())


def trigger(outcome: Outcome, tid: str = "t") -> tuple[TriggerDef, ...]:
    return (TriggerDef(TriggerId(tid), AfterTime(0), outcome),)


def test_183_valid_group_rules_validate():
    validate_rules(world((join(P1, GA, False), join(P2, own(P2, "a"), True), mark(P1, True, own(P1, "a"), at=5),
                          mark(P2, False, at=6))))
    validate_rules(world())


@kills(1)
def test_183_a_pooled_lane_is_a_ruled_lane():
    refused("lane g: a pooled lane is a ruled lane", lanes=lanes_with(LaneDef(G, False, pooled=True)))


def test_183_a_pooled_lane_has_no_group():
    two = (*lanes_with(LaneDef(G, True, pooled=True, group=G2)), LaneDef(G2, True, pooled=True))
    refused("lane g: a pooled lane has no group", lanes=two)


def test_183_only_a_ruled_lane_has_a_group():
    refused("lane q1: only a ruled lane has a group", lanes=lanes_with(LaneDef(Q1, False, group=G)))


@kills(2)
def test_183_a_group_is_a_pooled_lane():
    refused("lane p1: group p2 is not a pooled lane", lanes=lanes_with(LaneDef(P1, True, group=P2)))


@kills(3)
def test_183_a_card_on_a_pooled_lane_has_no_cap():
    capped = CardDef(GA, WORK, lane=G, cap=1, makes=(Flow(X, PER_SECOND),))
    refused("card ga: a card on a pooled lane has no cap", cards=(capped, *cards()[1:]))


def test_183_a_pooled_card_with_xp_is_refused_as_a_ruled_lane_card_that_trains_a_skill():
    trains = CardDef(GA, WORK, lane=G, skill=SkillId("k"), xp_per_hour=PER_SECOND)
    refused("a card on a ruled lane trains no skill", cards=(trains, *cards()[1:]))


@kills(4)
def test_183_a_start_of_a_pooled_card_is_refused():
    refused("taps ga, a card on a pooled lane", triggers=trigger(Outcome(starts=(GA,))))


def test_183_an_install_of_a_pooled_card_is_refused():
    refused("taps ga, a card on a pooled lane", triggers=trigger(Outcome(orders=(RuleInstall(GA),))))


def _queued_pooled_card() -> dict[str, Any]:
    answers = (AnswerDef(AnswerId("yes"), Outcome(queues=(GA,))), AnswerDef(AnswerId("no")))
    return {"offers": (OfferDef(OfferId("o"), answers),)}


def test_183_a_queue_of_a_pooled_card_is_refused():
    with pytest.raises(InvalidRulesError):
        validate_rules(world(check=False, **_queued_pooled_card()))


@pytest.mark.xfail(strict=True, reason="finding: the queue's own rule ('a queued one-off is a hands card with a cap') "
                   "fires first, so the listed message for a queued pooled card is never given")
def test_183_a_queue_of_a_pooled_card_names_the_pooled_lane():
    refused("taps ga, a card on a pooled lane", **_queued_pooled_card())


def test_183_a_pooled_lane_never_leaves():
    refused("leaves g, a pooled lane, which is never a person", triggers=trigger(Outcome(leaves=(Leave(G),))))


@kills(5)
def test_183_only_a_trigger_or_an_answer_marks_a_person():
    card = replace(cards()[2], outcome=Outcome(marks=(Mark(P1, False),)))
    refused("only a trigger's or an answer's outcome marks a person", cards=(*cards()[:2], card, *cards()[3:]))


def test_183_a_card_completion_that_finishes_with_a_mark_is_refused_too():
    card = replace(cards()[2], finished=Outcome(marks=(Mark(P1, False),)))
    refused("only a trigger's or an answer's outcome marks a person", cards=(*cards()[:2], card, *cards()[3:]))


def test_183_a_mark_names_a_declared_persons_lane():
    refused("marks zz, which is not a declared person's lane", triggers=trigger(Outcome(marks=(Mark(LaneId("zz"), True),))))


def test_183_a_pooled_lane_is_not_a_declared_persons_lane():
    refused("marks g, which is not a declared person's lane", triggers=trigger(Outcome(marks=(Mark(G, True),))))


@kills(6)
def test_183_an_unmark_needs_a_group():
    refused("unmarks q1, which has no group", triggers=trigger(Outcome(marks=(Mark(Q1, False),))))


@kills(7)
@pytest.mark.parametrize("card", [GA, off(P1), CardId("nope")])
def test_183_a_marks_card_is_an_uncapped_card_on_the_lane(card: CardId):
    refused("marks p1 with " + card + ", which is not an uncapped card on the lane",
            triggers=trigger(Outcome(marks=(Mark(P1, True, card),))))


@kills(8)
def test_183_a_join_of_a_pooled_lane_is_not_valid():
    refused("a join is not valid", triggers=trigger(Outcome(joins=(Join(G, TOWN, GA),))))


def test_183_an_unmarked_join_needs_a_group():
    refused("a join is not valid", triggers=(join(Q1, GA, False),))


@pytest.mark.parametrize("card", [own(P1, "a"), off(P1), CardId("nope")])
def test_183_an_unmarked_joins_card_is_an_uncapped_card_on_the_group(card: CardId):
    refused("a join is not valid", triggers=(join(P1, card, False),))
