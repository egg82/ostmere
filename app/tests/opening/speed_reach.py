"""Two figures for the opening's readout (report.py), never checks: how big each skill's track nodes are, and which cards a
later phase's speed pay reaches beyond its own skill's (docs/design/sim-invariants.md, O19 and O20). Both are tuning and
taste; what must hold of a node or a pay is kept by the engine's nodechecks and `check_phase_pays`."""
from collections import Counter

from ashfall_app.opening.schema import Opening


def node_size_lines(o: Opening) -> list[str]:
    """Per skill, how many nodes there are at each size in basis points per rank."""
    skills = dict.fromkeys(n.skill for n in o.nodes)
    out: list[str] = []
    for skill in skills:
        sizes = Counter(n.per_rank_bp for n in o.nodes if n.skill == skill)
        out.append(f"  {skill:14s} " + ", ".join(f"{k}bp x{v}" for k, v in sorted(sizes.items())))
    return out


def reach_lines(o: Opening) -> list[str]:
    """Per skill with a later-phase table, the cards its speed pays make faster that train another skill."""
    trains = {c.id: c.skill for c in o.cards}
    out: list[str] = []
    for pp in o.phase_pays:
        beyond = [f"{s.id} ({trains[s.id]})" for s in pp.speed if trains[s.id] != pp.skill]
        out.append(f"  {pp.skill:14s} " + (f"also speeds {', '.join(beyond)}" if beyond else "speeds only its own skill's cards"))
    return out
