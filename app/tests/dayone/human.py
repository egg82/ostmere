"""The human-paced player: day one played at a person's speed, on the same DayOnePlayer the routes use. A tap follows a
reaction of seconds, a glance waits out the reading of every line that arrived since the last, and the visits are a
seeded spread across a waking day. A visit ends once nothing is left to act on and nothing is unread
, or at session_s. Every number is a threshold in human_thresholds.toml,
beside its source.

It is a model of a first-time player's time, not a sharp one: knobs are the typical route's. What it records is read
by human_flags.py. Played once per session like any route (docs/engineering.md, "Fast from the start")."""
import math
import random
import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from ashfall_app.engine import Rules, View
from tests.dayone.player import DayOnePlayer
from tests.dayone.schedules import HORIZON_S, HOUR, Schedule, Visit
from tests.opening.playthrough import opening, opening_rules

THRESHOLDS = Path(__file__).with_name("human_thresholds.toml")
DOCS = Path(__file__).resolve().parents[3] / "docs"
DESIGN_CHOICE = "design choice"


@dataclass(frozen=True)
class Threshold:
    value: float
    unit: str
    source: str
    note: str


@dataclass(frozen=True)
class Thresholds:
    entries: dict[str, Threshold]
    dead_gap: str
    """The name of the threshold a stretch with nothing notable is held to."""

    def v(self, name: str) -> float:
        return self.entries[name].value

    def dead_gap_s(self) -> float:
        return self.v(self.dead_gap)

    def unsourced(self) -> list[str]:
        """Thresholds whose source is neither `design choice` nor `docs/research/<file>.md#<heading>` naming a file that
        exists and holds that heading line."""
        return [n for n, t in self.entries.items() if t.source != DESIGN_CHOICE and not _cites(t.source)]


def _cites(source: str) -> bool:
    path, _, heading = source.partition("#")
    file = DOCS.parent / path
    return (path.startswith("docs/research/") and path.endswith(".md") and bool(heading) and file.is_file()
            and heading in file.read_text().splitlines())


@cache
def thresholds(path: Path = THRESHOLDS) -> Thresholds:
    raw = tomllib.loads(path.read_text())
    entries = {n: Threshold(float(e["value"]), str(e["unit"]), str(e["source"]), str(e.get("note", "")))
               for n, e in raw["threshold"].items()}
    return Thresholds(entries, str(raw["model"]["dead_gap"]))


def human_schedule(seed: int, th: Thresholds) -> Schedule:
    """The visits: waking gaps of waking_h / visits_per_day, each a seeded draw within the jitter, and a night in place
    of every round(visits_per_day)-th gap."""
    rng = random.Random(f"human-{seed}")
    per_day, base, j = round(th.v("visits_per_day")), th.v("waking_h") / th.v("visits_per_day"), th.v("return_jitter")
    length = round(th.v("session_s"))
    visits = [Visit(0, length)]
    n = 0
    while visits[-1].start < HORIZON_S:
        n += 1
        gap_h = th.v("night_h") if n % per_day == 0 else base * rng.uniform(1 - j, 1 + j)
        visits.append(Visit(visits[-1].start + visits[-1].length + round(gap_h * HOUR), length))
    return Schedule("human", tuple(visits))


@dataclass
class HumanPlayer(DayOnePlayer):
    wpm: float = 238.0
    read_lines: int = 0
    """How many of `lines` have been read."""

    def glance(self) -> int:
        """The reaction, plus the time to read what arrived since the last glance (a return reads all of what landed
        away)."""
        text = opening().text
        words = sum(len(text[ln.key].split()) for ln in self.lines[self.read_lines:])
        self.read_lines = len(self.lines)
        return super().glance() + math.ceil(words / self.wpm * 60)

    def leaves(self) -> bool:
        """Nothing to act on (no ready step, no offer): the player reads what is unread and watches a tap of theirs
        land if it lands within the dead gap, then leaves (orchestrator, 2026-10-23). session_s is
        only a visit's longest."""
        if self.read_lines < len(self.lines):
            self._advance_through(self.save.time + self.glance())
            return False
        return not lands_within(self.view(), self.rules, self.save.time, thresholds().dead_gap_s())


def lands_within(v: View, rules: Rules, now: int, gap_s: float) -> bool:
    """A tap of the player's lands within gap_s of now: with nothing else to act on, the player stays to watch it
    rather than leave. A townsperson's lane (LaneDef.ruled) is not the player's, and its taps are
    never waited for. The one leave rule, shared by every player that leaves a visit early."""
    theirs = {d.id for d in rules.lanes if d.ruled}
    return any(b.card is not None and b.lane not in theirs and b.completes_at is not None
               and b.completes_at - now <= gap_s for b in v.lanes)


@cache
def human_day(seed: int = 0) -> HumanPlayer:
    th = thresholds()
    p = HumanPlayer(opening_rules(), seed=seed, schedule=human_schedule(seed, th), wpm=th.v("reading_wpm"),
                    reaction=(round(th.v("reaction_practised_s")), round(th.v("reaction_first_time_s"))))
    p.play_day()
    return p
