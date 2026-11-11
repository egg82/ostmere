"""The entries a skill's prestige picks hold in the stack (DESIGN.txt, "PRESTIGE PHASES"): derived from the picks
wherever the stack is read, never stored, as heldentries.py's are. So an UndoPick is exact: the entry follows the
picks, and nothing in save.modifiers has to be found and taken out."""
from .ids import NodeId, SkillId, SourceId
from .index import derived
from .modifiers import Modifier, ModifierKind
from .nodes import NODE_PREFIX, NodeDef
from .rules import Rules
from .state import Save
from .units import BP

type _Picks = tuple[tuple[SkillId, tuple[NodeId, ...]], ...]


def pick_source(node: NodeId) -> SourceId:
    """The source of `node`'s rank entry: nodes.NODE_PREFIX followed by the node's id, so explain() names the node."""
    return SourceId(f"{NODE_PREFIX}{node}")


def nodes_by_id(rules: Rules) -> dict[NodeId, NodeDef]:
    """rules.nodes by id. Callers must not mutate it."""
    return derived(rules, "_nodes_by_id", lambda r: {n.id: n for n in r.nodes})


def ranks(save: Save, node: NodeDef) -> int:
    """How many of node.skill's picks name the node."""
    return next((st.phase.picks.count(node.id) for st in save.skills if st.skill == node.skill), 0)


def held(save: Save, node: NodeDef) -> int:
    """How many ranks of node.skill's track the node holds or has parked on it (PhaseState.parked): what keeps it off
    the menu once full. `ranks` counts only the ranks in play."""
    st = next((s.phase for s in save.skills if s.skill == node.skill), None)
    return 0 if st is None else st.picks.count(node.id) + sum(p.node == node.id for p in st.parked)


def pick_entries(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    """One entry per node with at least one rank taken (prestige.ranks_taken), in rules.nodes order:
    Modifier(node.target, MUL_BP, BP + n * node.per_rank_bp, pick_source(node.id)) for n ranks. Ranks within a node
    add; nodes compound with each other and with every other multiplier on the target (modifiers.modified_rate).
    They join the base stack after the held entries (gates.base_stack), so they reach every line the target names,
    tapped, mixed or run by a lane. Empty with rules.prestige None or no picks. Reads only the skills' picks, never a
    rate, so building the stack never recurses.

    Equal picks give the very same tuple, so a memo that compares the stack's parts by identity keeps what it built
    while the picks are unchanged."""
    if rules.prestige is None:
        return ()
    picks: _Picks = tuple((st.skill, st.phase.picks) for st in save.skills if st.phase.picks)
    if not picks:
        return ()
    kept = derived(rules, "_pick_entries", lambda r: dict[_Picks, tuple[Modifier, ...]]())
    found = kept.get(picks)
    if found is None:
        if len(kept) >= 256:
            kept.clear()
        found = kept[picks] = _entries(save, rules)
    return found


def _entries(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    out: list[Modifier] = []
    for node in rules.nodes:
        n = ranks(save, node)
        if n > 0:
            out.append(Modifier(node.target, ModifierKind.MUL_BP, BP + n * node.per_rank_bp, pick_source(node.id)))
    return tuple(out)
