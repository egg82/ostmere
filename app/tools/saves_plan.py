"""The full run's chapter-save jobs, planned from each chapter's measured cost (tools/ci_costs.json), not from lists.

Run from app/: PYTHONPATH=. python -m tools.saves_plan   prints the plan as JSON; CI's `saves-plan` job reads it, and
exits 1 when a job is predicted over TARGET_S or the chains need more links than the workflow has ranks.

The three kinds of job (tools/chapter_saves.py writes each by its part's name):
  links     a route's chain of saved ends, in chain order, cut into links; link k of every route runs in rank k, after
            rank k-1 (a link starts from the ends the link before uploaded)
  rebased   typical's rebased saves, one group of chapters per job
  readings  typical's heavy-step readings, groups of (chapter, first step, after) spans, one job each
Chapters pack in order into a job until its predicted time would pass TARGET_S, the job's cap less a margin. A chapter or
step with no row in the table is planned at the table's `unmeasured` figure and named in `estimated`.
"""
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CAP_MIN = 30
"""The `timeout-minutes` of every job planned here (tests/tools/test_ci_budget.py reads ci.yml against it)."""
MARGIN_MIN = 18
"""What a job is kept short of its cap: measured runs of one job differ by up to 2.5 times, and the table holds the worst of
three."""
TARGET_S = (CAP_MIN - MARGIN_MIN) * 60
RANKS = 12
"""The links of a route the workflow has jobs for (one `chapter-saves-link-k` job each)."""
LINK_LOAD_S = 20
"""A link after the first first loads the saved end before it; a table figure measured mid-link does not include that."""
TABLE = Path(__file__).with_name("ci_costs.json")

Span = tuple[str, int, int | None]
"""(chapter, first heavy step, the one after the last or None for all the rest): a slice of verdicts.heavy_steps."""


@dataclass(frozen=True)
class Link:
    part: str
    route: str
    chapters: tuple[str, ...]
    rank: int
    after: str
    """The part whose ends this link starts from, "" for the first link."""
    predicted_s: int


@dataclass(frozen=True)
class Group:
    part: str
    chapters: tuple[str, ...]
    predicted_s: int


@dataclass(frozen=True)
class Reading:
    part: str
    spans: tuple[Span, ...]
    predicted_s: int


@dataclass(frozen=True)
class Plan:
    links: tuple[Link, ...]
    rebased: tuple[Group, ...]
    readings: tuple[Reading, ...]
    estimated: tuple[str, ...] = field(default=())
    """What was planned at the table's `unmeasured` figure: "ends:route:chapter", "rebased:chapter", "readings:chapter"."""

    def jobs(self) -> list[tuple[str, int]]:
        """(part, predicted seconds) of every job planned."""
        return [(j.part, j.predicted_s) for j in (*self.links, *self.rebased, *self.readings)]

    def ranks(self) -> int:
        return max((link.rank for link in self.links), default=0)


def load(path: Path = TABLE) -> dict[str, Any]:
    return dict(json.loads(path.read_text()))


def pack(items: list[tuple[str, int]], start: int, later: int | None = None, target: int = TARGET_S) -> list[list[tuple[str, int]]]:
    """`items` (name, seconds) in order, cut into runs whose sum plus the run's start cost (`start` for the first, `later`
    after it, default the same) stays within `target`; an item over it alone is a run of its own."""
    runs: list[list[tuple[str, int]]] = []
    total = 0
    for name, seconds in items:
        if runs and total + seconds <= target:
            runs[-1].append((name, seconds))
            total += seconds
        else:
            total = (later if later is not None and runs else start) + seconds
            runs.append([(name, seconds)])
    return runs


def plan(table: dict[str, Any], chains: dict[str, list[str]], rebased: list[str], readings: list[str]) -> Plan:
    """The jobs for `chains` (route -> its chapters with a saved end, in order), the chapters with a rebased save and those
    with readings, each in order."""
    over = int(table["job_overhead_s"])
    estimated: list[str] = []
    links: list[Link] = []
    for route, chapters in chains.items():
        items: list[tuple[str, int]] = []
        for c in chapters:
            known = table["ends"].get(route, {}).get(c)
            if known is None:
                estimated.append(f"ends:{route}:{c}")
            items.append((c, int(known if known is not None else table["unmeasured"]["ends"][route])))
        done = ""
        for k, run in enumerate(pack(items, over, over + LINK_LOAD_S), 1):
            part = f"{route}-{k}"
            seconds = over + sum(s for _, s in run) + (LINK_LOAD_S if k > 1 else 0)
            links.append(Link(part, route, tuple(c for c, _ in run), k, done, seconds))
            done = part
    costs: list[tuple[str, int]] = []
    for c in rebased:
        if c not in table["rebased"]:
            estimated.append(f"rebased:{c}")
        costs.append((c, int(table["rebased"].get(c, table["unmeasured"]["rebased"]))))
    groups = [Group(f"rebased-{run[0][0]}", tuple(c for c, _ in run), over + sum(s for _, s in run))
              for run in pack(costs, over)]
    return Plan(tuple(links), tuple(groups), tuple(plan_readings(table, readings, estimated)), tuple(estimated))


def steps_of(table: dict[str, Any], chapter: str) -> dict[str, Any]:
    """The chapter's readings row: its setup and each heavy step's seconds, or the `unmeasured` row."""
    return dict(table["readings"].get(chapter, table["unmeasured"]["readings"]))


def heavy_count(table: dict[str, Any], chapter: str) -> int:
    return len(steps_of(table, chapter)["steps_s"])


def plan_readings(table: dict[str, Any], chapters: list[str], estimated: list[str]) -> list[Reading]:
    """Each chapter's heavy steps in order, cut into jobs; a job pays a chapter's setup (reaching typical's play through
    it) once, and a chapter's last span is open, so a step content adds is read by it."""
    over = int(table["job_overhead_s"])
    out: list[Reading] = []
    spans: list[Span] = []
    total = 0
    for chapter in chapters:
        row = steps_of(table, chapter)
        if chapter not in table["readings"]:
            estimated.append(f"readings:{chapter}")
        for i, seconds in enumerate(row["steps_s"]):
            joined = bool(spans) and spans[-1][0] == chapter
            extra = int(seconds) + (0 if joined else int(row["setup_s"]))
            if spans and total + extra > TARGET_S:
                if joined:
                    spans[-1] = (chapter, spans[-1][1], i)
                out.append(Reading(f"readings-{spans[0][0]}-{spans[0][1]}", tuple(spans), total))
                spans, joined, extra = [], False, int(seconds) + int(row["setup_s"])
            if not spans:
                total = over
            if not joined:
                spans.append((chapter, i, None))
            total += extra
    if spans:
        out.append(Reading(f"readings-{spans[0][0]}-{spans[0][1]}", tuple(spans), total))
    return out


def today() -> Plan:
    """The plan for the chapters and routes the code has now."""
    from tests.weektwo import keys, rebased
    from tests.weektwo.routes import CHAPTERS, SAVED
    table = load()
    chains = {route: [c for c, names in SAVED.items() if route in names] for route in table["ends"]}
    return plan(table, chains, [c for c in keys.ORDER if c in rebased.OLD], list(CHAPTERS))


def matrix(p: Plan) -> dict[str, Any]:
    """What CI reads: each rank's legs (an idle leg where a rank has none, so every rank's job runs and passes), the
    rebased and readings parts."""
    ranks: list[list[dict[str, str]]] = []
    for k in range(1, RANKS + 1):
        legs = [{"part": link.part, "names": link.part, "after": link.after} for link in p.links if link.rank == k]
        ranks.append(legs or [{"part": "idle", "names": "", "after": ""}])
    return {"ranks": ranks, "rebased": [g.part for g in p.rebased], "readings": [r.part for r in p.readings],
            "estimated": list(p.estimated)}


def problems(p: Plan) -> list[str]:
    found = [f"{part} is predicted {math.ceil(s / 60)} min, over the {TARGET_S // 60} min target" for part, s in p.jobs() if s > TARGET_S]
    if p.ranks() > RANKS:
        found.append(f"the chains need {p.ranks()} links, the workflow has {RANKS} ranks: add a chapter-saves-link job")
    return found


def main() -> int:
    p = today()
    print(json.dumps(matrix(p)))
    for part, s in sorted(p.jobs(), key=lambda j: -j[1]):
        print(f"event=saves_plan.job part={part} predicted_s={s}", file=sys.stderr)
    for e in p.estimated:
        print(f"event=saves_plan.estimated {e}", file=sys.stderr)
    found = problems(p)
    for line in found:
        print(f"event=saves_plan.problem {line}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
