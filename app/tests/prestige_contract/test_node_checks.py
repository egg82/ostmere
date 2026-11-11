"""What makes the rules' prestige and nodes valid (nodechecks.check_nodes, called by validate_rules), and what the
content loader lets a node say (opening/prestige.py). Each refusal is one change to rules that pass first."""
from dataclasses import replace

import pytest
from pydantic import ValidationError

from ashfall_app.engine import (
    BP, HANDS, CardId, FlowKind, InvalidRulesError, LaneSpeed, NodeDef, PrestigeDef, RateRef, Rules, SideStrength,
    SkillId, StoreCap, StoreId, ThreatStrength, Unlock, UnlockKind, WorkRef, validate_rules,
)
from ashfall_app.engine.ids import SideId, ThreatId
from ashfall_app.engine.nodes import NodeTarget
from ashfall_app.engine.nodechecks import check_nodes
from ashfall_app.opening.prestige import NodeChangeEntry, NodeEntry, PrestigeEntry, node_def, prestige_def
from prestige_world import HONE, J, K, N1, OTHER, TRAIN, WOOD, rules


def one(**change: object) -> NodeDef:
    return replace(NodeDef(N1, K, WorkRef(OTHER), ranks=2, per_rank_bp=BP // 10), **change)


def with_node(node: NodeDef) -> Rules:
    return replace(rules(), nodes=(node,))


def test_the_worlds_these_suites_share_are_valid():
    """Every rules variant the other tests build, so a test never passes or fails on a world that is itself invalid."""
    variants = [rules(), rules(100), rules(menu_size=3), replace(rules(), opening=(Unlock(UnlockKind.STORE, "wood"),)),
                replace(rules(), nodes=(replace(rules().nodes[0], ranks=1),))]
    for r in variants:
        check_nodes(r)
        validate_rules(r)


@pytest.mark.parametrize("target", [
    RateRef(OTHER, FlowKind.MAKE, WOOD), WorkRef(OTHER), StoreCap(WOOD),
], ids=["make", "work", "cap"])
def test_a_node_may_change_a_make_a_work_speed_or_a_cap_beyond_its_skill(target: NodeTarget):
    check_nodes(with_node(one(target=target)))


@pytest.mark.parametrize("node", [
    one(target=RateRef(OTHER, FlowKind.XP)),
    one(target=RateRef(OTHER, FlowKind.COST, WOOD)),
    one(target=LaneSpeed(HANDS)),
    one(target=SideStrength(SideId("s"))),
    one(target=ThreatStrength(ThreatId("t"))),
], ids=["xp", "cost", "lane-speed", "side-strength", "threat-strength"])
def test_a_node_aimed_at_xp_a_cost_lane_speed_or_a_strength_is_refused(node: NodeDef):
    with pytest.raises(InvalidRulesError):
        check_nodes(with_node(node))
    with pytest.raises(InvalidRulesError):
        validate_rules(with_node(node))


@pytest.mark.parametrize("node", [
    one(target=WorkRef(HONE)),
    one(target=RateRef(HONE, FlowKind.MAKE, WOOD)),
    one(target=RateRef(TRAIN, FlowKind.MAKE, WOOD)),
], ids=["own-card-work", "own-card-make", "own-standing"])
def test_a_node_acting_on_its_own_skills_work_is_refused(node: NodeDef):
    """HONE and TRAIN train K; J's node on the same standing action is the control that only the skill decides it."""
    check_nodes(with_node(replace(node, skill=J)))
    with pytest.raises(InvalidRulesError):
        check_nodes(with_node(node))


@pytest.mark.parametrize("node", [
    one(target=RateRef(OTHER, FlowKind.MAKE, StoreId("ghost"))),
    one(target=WorkRef(CardId("ghost-card"))),
    one(target=StoreCap(StoreId("ghost"))),
    one(skill=SkillId("ghost-skill")),
    one(ranks=0),
    one(per_rank_bp=0),
], ids=["unknown-store-in-make", "unknown-card", "unknown-store-cap", "unknown-skill", "zero-ranks", "zero-per-rank"])
def test_unknown_ids_and_empty_ranks_are_refused(node: NodeDef):
    with pytest.raises(InvalidRulesError):
        check_nodes(with_node(node))


def test_duplicate_node_ids_are_refused():
    with pytest.raises(InvalidRulesError):
        check_nodes(replace(rules(), nodes=(one(), one(skill=J))))


def test_nodes_need_prestige():
    with pytest.raises(InvalidRulesError):
        check_nodes(replace(rules(), prestige=None))
    check_nodes(replace(rules(), prestige=None, nodes=()))


@pytest.mark.parametrize("prestige", [
    PrestigeDef(1, 100, 2), PrestigeDef(5, 100, 2), PrestigeDef(3, 0, 2), PrestigeDef(3, 100, 1), PrestigeDef(3, 100, 4),
], ids=["top-level-1", "top-past-curve", "no-window", "menu-1", "menu-4"])
def test_a_prestige_table_out_of_range_is_refused(prestige: PrestigeDef):
    with pytest.raises(InvalidRulesError):
        check_nodes(replace(rules(), prestige=prestige))


@pytest.mark.parametrize("prestige", [PrestigeDef(2, 1, 2), PrestigeDef(4, 10**6, 3)], ids=["lowest", "highest"])
def test_a_prestige_table_at_its_bounds_is_valid(prestige: PrestigeDef):
    check_nodes(replace(rules(), prestige=prestige))


# The loader: another way a node cannot be aimed at XP or a lane.

@pytest.mark.parametrize("change", [{"target": "xp", "id": "other"}, {"target": "lane", "id": "hands"},
                                    {"target": "cost", "id": "other", "store": "wood"}])
def test_the_loader_has_no_target_for_xp_a_lane_or_a_cost(change: dict[str, str]):
    with pytest.raises(ValidationError):
        NodeChangeEntry.model_validate(change)


@pytest.mark.parametrize("fields", [
    {"top_level": 1, "carry_window_s": 10, "menu_size": 2}, {"top_level": 3, "carry_window_s": 0, "menu_size": 2},
    {"top_level": 3, "carry_window_s": 10, "menu_size": 1}, {"top_level": 3, "carry_window_s": 10, "menu_size": 4},
], ids=["top-level", "window", "menu-low", "menu-high"])
def test_the_loaders_prestige_table_refuses_out_of_range(fields: dict[str, int]):
    with pytest.raises(ValidationError):
        PrestigeEntry.model_validate(fields)


def test_the_loaders_prestige_table_converts():
    assert prestige_def(None) is None
    entry = PrestigeEntry.model_validate({"top_level": 3, "carry_window_s": 10, "menu_size": 3})
    assert prestige_def(entry) == PrestigeDef(3, 10, 3)


@pytest.mark.parametrize("change, target", [
    ({"target": "make", "id": "other", "store": "wood"}, RateRef(OTHER, FlowKind.MAKE, WOOD)),
    ({"target": "make", "id": "train", "store": "wood"}, RateRef(TRAIN, FlowKind.MAKE, WOOD)),
    ({"target": "work", "id": "other"}, WorkRef(OTHER)),
    ({"target": "cap", "id": "wood"}, StoreCap(WOOD)),
], ids=["make-card", "make-standing", "work", "cap"])
def test_the_loader_converts_each_target_kind(change: dict[str, str], target: NodeTarget):
    entry = NodeEntry.model_validate({"id": "n1", "skill": "k", "label_key": "x", "changes": change, "ranks": 2, "per_rank_bp": 500})
    assert node_def(entry, {"other", "hone"}) == NodeDef(N1, K, target, 2, 500)


def test_the_loader_refuses_an_unknown_field_and_empty_ranks():
    base = {"id": "n1", "skill": "k", "label_key": "x", "changes": {"target": "work", "id": "other"}, "ranks": 2, "per_rank_bp": 500}
    NodeEntry.model_validate(base)
    for bad in ({"ranks": 0}, {"per_rank_bp": 0}, {"extra": 1}):
        with pytest.raises(ValidationError):
            NodeEntry.model_validate(base | bad)
