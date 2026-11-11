"""What makes the rules' prestige and nodes valid (nodes.py). validate_rules (rules.py) calls it."""
from typing import TYPE_CHECKING

from .errors import InvalidRulesError
from .ids import Runner, SkillId
from .modifiers import FlowKind, RateRef, StoreCap, WorkRef
from .nodes import NodeDef, PrestigeDef

if TYPE_CHECKING:
    from .rules import Rules


def check_nodes(rules: "Rules") -> None:
    """Raise InvalidRulesError unless rules.prestige and rules.nodes are valid:
    - rules.prestige, when set: 2 <= top_level <= len(curve.thresholds) + 1, carry_window_s >= 1, menu_size 2 or 3;
    - any node at all needs rules.prestige set;
    - node ids unique; each node's skill known; ranks >= 1 and per_rank_bp >= 1;
    - each target a RateRef of kind MAKE on a known runner and store, a WorkRef of a known card, or a StoreCap of a
      known store: a RateRef of kind XP or COST, a LaneSpeed, a SideStrength and a ThreatStrength are refused, since
      a node that sped XP (a lane's speed joins every line on the lane, XP included) would make levels come sooner;
    - each target outside its node's skill: a RateRef's runner and a WorkRef's card do not train it."""
    if rules.prestige is not None:
        _check_prestige(rules.prestige, len(rules.curve.thresholds) + 1)
    _require(not rules.nodes or rules.prestige is not None, "nodes need rules.prestige")
    ids = [n.id for n in rules.nodes]
    _require(len(set(ids)) == len(ids), "duplicate node id")
    skills = {s.id for s in rules.skills}
    trains = _trains(rules)
    for node in rules.nodes:
        _check_node(node, skills, trains, rules)


def _check_prestige(p: PrestigeDef, max_level: int) -> None:
    _require(2 <= p.top_level <= max_level, "prestige top_level must be a level of the curve above 1")
    _require(p.carry_window_s >= 1, "prestige carry_window_s must be >= 1")
    _require(p.menu_size in (2, 3), "prestige menu_size must be 2 or 3")


def _trains(rules: "Rules") -> dict[Runner, SkillId | None]:
    """Each runner's skill: what its XP line trains (None: no skill)."""
    found: dict[Runner, SkillId | None] = {a.id: a.skill for a in rules.standing}
    return found | {c.id: c.skill for c in rules.cards}


def _check_node(node: NodeDef, skills: set[SkillId], trains: dict[Runner, SkillId | None], rules: "Rules") -> None:
    where = f"node {node.id}"
    _require(node.skill in skills, f"{where}: unknown skill")
    _require(node.ranks >= 1 and node.per_rank_bp >= 1, f"{where}: needs ranks >= 1 and per_rank_bp >= 1")
    owner = _owner(node.target, where, trains, rules)
    _require(owner != node.skill, f"{where}: changes its own skill's work; a node acts beyond its skill")


def _owner(target: object, where: str, trains: dict[Runner, SkillId | None], rules: "Rules") -> SkillId | None:
    """The skill whose work `target` changes (None for a cap), once it is a target a node may have. Takes object:
    rules built in code can hold any Target on a node, and only three kinds are a node's."""
    stores = {s.id for s in rules.stores}
    if isinstance(target, RateRef):
        _require(target.kind is FlowKind.MAKE, f"{where}: a node changes a make, never XP or a cost")
        _require(target.runner in trains and target.store in stores, f"{where}: unknown runner or store")
        return trains.get(target.runner)
    if isinstance(target, WorkRef):
        _require(target.card in {c.id for c in rules.cards}, f"{where}: unknown card")
        return trains.get(target.card)
    if isinstance(target, StoreCap):
        _require(target.store in stores, f"{where}: unknown store")
        return None
    raise InvalidRulesError(f"{where}: a node changes a make, a card's work or a cap, never a lane or a strength")


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidRulesError(message)
