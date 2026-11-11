"""Plain builders for the prestige contract tests: a small world with one skill that trains by itself (a standing
action, one XP unit a second), a card outside that skill for nodes to aim at, and a track of nodes per skill. Built from
the engine's public types only (DESIGN.txt, part "PRESTIGE PHASES"). No Hypothesis here.

With CURVE and TOP_LEVEL a phase spans SPAN = 300 XP, so K reaches phase 1's top at second 300 and the next phase's top
at second 600; XP never reaches that (its ceiling is one unit below, at second 599); the carry window decides
whether XP stops at the ceiling or earlier."""
from dataclasses import replace

from ashfall_app.engine import (
    ActionId, CardDef, CardId, Flow, FlowKind, NodeDef, NodeId, PacingCurve, PrestigeDef, Prestige, RateRef, Rules,
    Save, SkillDef, SkillId, StandingDef, StoreCap, StoreDef, StoreId, UndoPick, WorkRef, advance, decide, new_save,
    units, xp,
)

K, J = SkillId("k"), SkillId("j")
WOOD = StoreId("wood")
TRAIN = ActionId("train")
OTHER, HONE = CardId("other"), CardId("hone")
"""OTHER trains no skill, so nodes may aim at it; HONE trains K, so a K node may not."""

CURVE = PacingCurve((100, 300, 700))
TOP_LEVEL = 3
SPAN = 300
"""xp_for(CURVE, TOP_LEVEL)."""
WINDOW = 1000
"""A carry window longer than the time from one phase top to the next: XP stops at the ceiling."""

P = PrestigeDef(top_level=TOP_LEVEL, carry_window_s=WINDOW, menu_size=2)
"""The rules' prestige table, for the pure functions that read the curve and top level only."""

N1, N2, N3, N4, J1 = NodeId("n1"), NodeId("n2"), NodeId("n3"), NodeId("n4"), NodeId("j1")
MAKE_OTHER = RateRef(OTHER, FlowKind.MAKE, WOOD)
NODES = (
    NodeDef(N1, K, MAKE_OTHER, ranks=2, per_rank_bp=1000),
    NodeDef(N2, K, WorkRef(OTHER), ranks=1, per_rank_bp=2000),
    NodeDef(J1, J, StoreCap(WOOD), ranks=2, per_rank_bp=100),
    NodeDef(N3, K, StoreCap(WOOD), ranks=3, per_rank_bp=500),
    NodeDef(N4, K, MAKE_OTHER, ranks=1, per_rank_bp=5000),
)
"""K's track is n1, n2, n3, n4 (seven ranks), J's is j1; with menu_size 2 K's first menu is (n1, n2)."""
K_RANKS = 7
MENU_SIZE = 2


def rules(window: int = WINDOW, *, nodes: tuple[NodeDef, ...] = NODES, menu_size: int = MENU_SIZE) -> Rules:
    return Rules(
        stores=(StoreDef(WOOD, units(100)),),
        skills=(SkillDef(K), SkillDef(J)),
        standing=(StandingDef(TRAIN, makes=(Flow(WOOD, 1000),), skill=K, xp_per_hour=1),),
        curve=CURVE,
        cards=(CardDef(OTHER, 60, makes=(Flow(WOOD, 1000),)), CardDef(HONE, 60, skill=K, xp_per_hour=1)),
        prestige=replace(P, carry_window_s=window, menu_size=menu_size),
        nodes=nodes,
    )


def without_prestige(r: Rules) -> Rules:
    return replace(r, prestige=None, nodes=())


def at_second(r: Rules, t: int) -> Save:
    """A fresh save advanced to second t: K's XP is min(t, 300 + window, 600)."""
    return advance(new_save(r), r, t)


def click(save: Save, r: Rules, node: NodeId, t: int | None = None, skill: SkillId = K) -> Save:
    return decide(save, r, save.time if t is None else t, Prestige(skill, node))


def undo(save: Save, r: Rules, t: int | None = None, skill: SkillId = K) -> Save:
    return decide(save, r, save.time if t is None else t, UndoPick(skill))


def xp_now(save: Save, r: Rules, skill: SkillId = K) -> int:
    return xp(save, r, skill, save.time)
