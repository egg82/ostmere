"""The prestige verbs are wired into decide() as typed refusals, by hand only, and the codec carries a skill's phase
without changing any save that has none (engine prestigeverbs.py, state.PhaseState). Nodes refused at validation and
at the loader: engine nodechecks.py, opening/prestige.py."""
from dataclasses import replace
from typing import get_args

import pytest
from pydantic import ValidationError

from ashfall_app.engine import (
    BP, HANDS, AtLeast, CardDef, CardId, DeleteMix, FlowKind, InvalidRulesError, InvalidVerbError, LaneSpeed, MovePick, NodeDef, NodeId,
    Order, OrderVerb, PacingCurve, PhaseState, Prestige, PrestigeDef, PrestigeRefusal, PrestigeRefused, QueueEntry,
    RateRef, Rules, SaveMix, SetOrders, SetQueue, SkillDef, SkillId, StoreCap, StoreDef, StoreId, StoreValue, UndoPick,
    TapCard, Verb, WorkRef, decide, decode, encode, new_save, units, validate_rules, verb_from_json, verb_to_json,
)
from ashfall_app.engine.nodes import NodeTarget
from ashfall_app.opening.prestige import NodeChangeEntry

CRAFT, GATHER = SkillId("craft"), SkillId("gather")
WOOD = StoreId("wood")
CHOP = CardId("chop")
RULES = Rules(
    stores=(StoreDef(WOOD, units(10)),), skills=(SkillDef(CRAFT), SkillDef(GATHER)), standing=(),
    curve=PacingCurve((units(1), units(3))),
    cards=(CardDef(CHOP, 60, skill=GATHER, xp_per_hour=1000),),
)
PRESTIGE = PrestigeDef(top_level=2, carry_window_s=3600, menu_size=2)


def test_every_world_verb_has_an_order_but_the_prestige_verbs():
    verbs, orders = set(get_args(Verb.__value__)), set(get_args(OrderVerb.__value__))
    plan_edits = {SaveMix, DeleteMix, SetOrders, SetQueue}
    assert len(orders) > 1 and plan_edits <= verbs
    assert verbs - orders - plan_edits == {Prestige, UndoPick, MovePick}


@pytest.mark.parametrize("verb", [Prestige(CRAFT, NodeId("n")), UndoPick(CRAFT), MovePick(CRAFT, NodeId("n"), NodeId("m"))], ids=lambda v: type(v).__name__)
def test_decide_refuses_a_prestige_verb_under_rules_with_no_prestige(verb: Verb):
    with pytest.raises(PrestigeRefused) as found:
        decide(new_save(RULES), RULES, 0, verb)
    assert found.value.reason is PrestigeRefusal.NO_PRESTIGE
    assert isinstance(found.value, InvalidVerbError)


@pytest.mark.parametrize("verb", [Prestige(CRAFT, NodeId("n")), UndoPick(CRAFT), MovePick(CRAFT, NodeId("n"), NodeId("m"))], ids=lambda v: type(v).__name__)
def test_an_order_or_queue_entry_naming_one_is_refused_by_hand_only(verb: Prestige | UndoPick | MovePick):
    when = AtLeast(StoreValue(WOOD), 0, 0)
    tap = TapCard(CHOP)   # replaced by `verb` around the types, which refuse it; decide must too
    for plan in (SetOrders((replace(Order(when, tap), then=verb),)), SetQueue((replace(QueueEntry(tap, when), verb=verb),))):
        with pytest.raises(PrestigeRefused) as found:
            decide(new_save(RULES), RULES, 0, plan)
        assert found.value.reason is PrestigeRefusal.BY_HAND_ONLY


@pytest.mark.parametrize("verb", [Prestige(CRAFT, NodeId("n")), UndoPick(CRAFT), MovePick(CRAFT, NodeId("n"), NodeId("m"))], ids=lambda v: type(v).__name__)
def test_prestige_verbs_round_trip_in_the_decision_log(verb: Verb):
    assert verb_from_json(verb_to_json(verb)) == verb


def test_a_skill_in_its_first_phase_encodes_as_before_and_a_later_phase_round_trips():
    save = new_save(RULES)
    assert '"phase"' not in encode(save, RULES)
    later = PhaseState(phase=3, picks=(NodeId("a"), NodeId("b")), topped_at=40, click_level=2)
    moved = replace(save, skills=(replace(save.skills[0], phase=later), save.skills[1]))
    assert decode(encode(moved, RULES), RULES) == moved


def node(target: NodeTarget, skill: SkillId = CRAFT) -> NodeDef:
    return NodeDef(NodeId("n"), skill, target, ranks=3, per_rank_bp=BP // 10)


@pytest.mark.parametrize("target", [WorkRef(CHOP), RateRef(CHOP, FlowKind.MAKE, WOOD), StoreCap(WOOD)],
                         ids=["work", "make", "cap"])
def test_a_node_beyond_its_skill_is_valid(target: NodeTarget):
    validate_rules(replace(RULES, prestige=PRESTIGE, nodes=(node(target),)))


@pytest.mark.parametrize("rules", [
    replace(RULES, prestige=PRESTIGE, nodes=(node(RateRef(CHOP, FlowKind.XP)),)),
    replace(RULES, prestige=PRESTIGE, nodes=(node(RateRef(CHOP, FlowKind.COST, WOOD)),)),
    replace(RULES, prestige=PRESTIGE, nodes=(replace(node(WorkRef(CHOP)), target=LaneSpeed(HANDS)),)),
    replace(RULES, prestige=PRESTIGE, nodes=(node(WorkRef(CHOP), skill=GATHER),)),
    replace(RULES, nodes=(node(WorkRef(CHOP)),)),
    replace(RULES, prestige=replace(PRESTIGE, top_level=4)),
    replace(RULES, prestige=replace(PRESTIGE, menu_size=4)),
], ids=["xp", "cost", "lane", "own-skill", "no-prestige", "top-past-curve", "menu-size"])
def test_validation_refuses(rules: Rules):
    with pytest.raises(InvalidRulesError):
        validate_rules(rules)


@pytest.mark.parametrize("change", [{"target": "lane", "id": "hands"}, {"target": "xp", "id": "chop"}])
def test_the_loader_has_no_way_to_aim_a_node_at_xp_or_a_lane(change: dict[str, str]):
    with pytest.raises(ValidationError):
        NodeChangeEntry.model_validate(change)
