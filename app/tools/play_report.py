"""How far each player got and where it hurt, from the logfmt lines the app writes (event=game.request,
event=save.decision / save.advanced / save.opened, and event=game_leave: api/requestlog.py, saves/service.py,
client_errors.py).

Export the lines from Loki (adjust the selector to the Alloy labels):

    logcli query --since=24h --limit=100000 --quiet \\
      '{namespace="ashfall"} |~ "event=(game.request|save[.]|game_leave|client_error)"' > play.log
    python3 tools/play_report.py play.log        # or: ... | python3 tools/play_report.py -

Without logcli: `kubectl -n loki port-forward svc/loki 3100` and GET /loki/api/v1/query_range with the same query, a
day per request (limit 5000), printing each result's `values[][1]`. Needs Python 3.10+ (the system python3 is older).

A game is one save, by its id: its requests in order, and the game time its writes reached. Page loads are not tied to
saves (the leave beacon logs no id), so leaves are listed on their own.
"""
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

LONG_RUN = 5   # taps of one card in a row that count as a chore, `decisions.md`: "different steps, never one tap repeated"

_PAIR = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S*)')


def parse(line: str) -> dict[str, str]:
    """A logfmt line (anything before `ts=` such as a Loki timestamp is ignored) as a dict; {} when it has no event."""
    start = line.find("ts=")
    fields = {k: v.strip('"') for k, v in _PAIR.findall(line[start:] if start >= 0 else line)}
    return fields if "event" in fields else {}


def _int(fields: dict[str, str], key: str) -> int | None:
    value = fields.get(key, "")
    return int(value) if value.isdecimal() else None


@dataclass
class Chain:
    steps: int = 0   # decisions
    last_at: int = 0   # game time reached
    last_wall: int = 0
    last_target: str = ""
    longest_gap: int = 0
    gap_step: int = 0
    gap_target: str = ""
    failed: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors: int = 0
    runs: list[int] = field(default_factory=lambda: [])   # lengths of runs of one card tapped in a row (a run ends at any other decision)
    run_card: str = ""

    @property
    def longest_run(self) -> int:
        return max(self.runs, default=0)

    @property
    def long_runs(self) -> int:
        return sum(1 for n in self.runs if n >= LONG_RUN)


def build_chains(events: Iterable[dict[str, str]]) -> list[Chain]:
    """One Chain per save id, in the order saves first appear: its requests (game.request) and the game time its
    writes reached (save.* game_at)."""
    chains: dict[str, Chain] = {}
    for e in events:
        save = e.get("save", "")
        if not save:
            continue
        chain = chains.setdefault(save, Chain())
        if e["event"] == "game.request":
            _apply(chain, e)
        elif e["event"].startswith("save."):
            chain.last_at = max(chain.last_at, _int(e, "game_at") or 0)
    return list(chains.values())


def _apply(chain: Chain, r: dict[str, str]) -> None:
    if int(r.get("status", "200")) >= 400:
        chain.errors += 1
        return
    chain.last_wall = max(chain.last_wall, _int(r, "wall_s") or 0)
    if r.get("decision", "none") in ("none", "advance"):
        return
    chain.steps += 1
    chain.last_target = r.get("target", r["decision"])
    _note_run(chain, r)
    gap = _int(r, "gap_s")
    if gap is not None and gap > chain.longest_gap:
        chain.longest_gap, chain.gap_step, chain.gap_target = gap, chain.steps, chain.last_target
    if r.get("failed") == "1":
        chain.failed[chain.last_target] += 1


def _note_run(chain: Chain, r: dict[str, str]) -> None:
    card = r.get("target", "") if r["decision"] == "tap_card" else ""
    if card and card == chain.run_card:
        chain.runs[-1] += 1
    elif card:
        chain.runs.append(1)
    chain.run_card = card


def report(lines: Iterable[str]) -> str:
    events = [f for f in map(parse, lines) if f]
    requests = [f for f in events if f["event"] == "game.request" and f.get("save")]
    leaves = [f for f in events if f["event"] == "game_leave"]
    errors = [f for f in events if f["event"] == "client_error"]
    out = [f"{len(requests)} requests, {len(leaves)} leaves, {len(errors)} client errors"]
    for i, c in enumerate(build_chains(events), 1):
        fails = ", ".join(f"{t} x{n}" for t, n in sorted(c.failed.items())) or "none"
        out.append(
            f"game {i}: {c.steps} decisions, game time {c.last_at}, {c.last_wall}s on the clock, last {c.last_target or '-'}; "
            f"longest gap {c.longest_gap}s before decision {c.gap_step} ({c.gap_target or '-'}); failed taps: {fails}; "
            f"longest run of one card tapped {c.longest_run}, runs of {LONG_RUN}+ {c.long_runs}; "
            f"refused/errored requests: {c.errors}")
    for lv in leaves:
        end = "reached the end" if lv.get("reached_end") == "1" else "left before the end"
        out.append(
            f"leave: {end} after {lv.get('since_begin_s', '?')}s, game time {lv.get('game_time', '?')}, "
            f"{lv.get('decisions', '?')} decisions, last one-off {lv.get('last_project') or '-'}")
    ends = sorted(int(v) for lv in leaves if lv.get("reached_end") == "1" if (v := lv.get("since_begin_s", "")).isdecimal())
    out.append(f"wall seconds to the end (as seen at leave, upper bound): {ends or 'none reached it'}")
    return "\n".join(out)


def main(argv: list[str]) -> None:
    source = argv[1] if len(argv) > 1 else "-"
    lines = sys.stdin if source == "-" else open(source, encoding="utf-8")
    print(report(lines))


if __name__ == "__main__":
    main(sys.argv)
