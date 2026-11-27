"""The prestige tracks' readout: per skill, how many of its ranks bring something new and how many repeat. A rank is new
when it is the first of a node whose change no earlier node of the track made; every other rank repeats (a further rank
of the same node, or a node changing what an earlier one did). Taste, so it reports and fails nothing (docs/design/
sim-invariants.md). Skills, node ids and counts only (CLAUDE.md, "Never spoil the owner").

    python -m tests.rules.play.tracks_readout     # from app/: print it
"""
import sys
from collections import defaultdict

from ashfall_app.rules.prestige import NodeEntry
from ashfall_app.rules.schema import load_opening

NAMES = ("tracks",)


def _change(n: NodeEntry) -> tuple[str, str, str | None]:
    return (n.changes.target, n.changes.id, n.changes.store)


def render(nodes: list[NodeEntry]) -> str:
    """One line per skill, in file order: nodes, ranks, ranks new and repeated, and the nodes of more than one rank or
    repeating an earlier node's change."""
    tracks: dict[str, list[NodeEntry]] = defaultdict(list)
    for n in nodes:
        tracks[n.skill].append(n)
    lines = ["skill        nodes ranks  new repeat  multi-rank nodes; nodes repeating an earlier change"]
    for skill, track in tracks.items():
        seen: set[tuple[str, str, str | None]] = set()
        new, repeated = 0, 0
        again: list[str] = []
        for n in track:
            fresh = _change(n) not in seen
            seen.add(_change(n))
            new += fresh
            repeated += n.ranks - fresh
            if not fresh:
                again.append(n.id)
        multi = [f"{n.id} x{n.ranks}" for n in track if n.ranks > 1]
        lines.append(f"{skill:12s} {len(track):5d} {sum(n.ranks for n in track):5d} {new:4d} {repeated:6d}  "
                     f"{', '.join(multi) or '-'}; {', '.join(again) or '-'}")
    return "\n".join(lines)


def readouts() -> dict[str, str]:
    return {"tracks": render(load_opening().nodes)}


if __name__ == "__main__":
    print(readouts()["tracks"])
    sys.exit(0)
