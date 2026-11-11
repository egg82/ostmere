"""The story's shape on a played route, checked by the content team's own tool (content/team/flatcheck.py) fed the
route's hours and visits, and the rebase route: the opening's golden ended saves loaded into today's rules after time
away. Both name story ids, hours and visits only."""
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from ashfall_app.engine import Line, Rules, Save, advance_logged, next_event, rebase_logged
from ashfall_app.opening.renames import engine_renames, load_renames
from tests.dayone.beats import BEATS_YAML, STORY, landed
from tests.dayone.checks import absence_unlocks, one_per_moment, opens
from tests.dayone.player import DayOnePlayer
from tests.opening.playthrough import opening_rules

FLATCHECK = BEATS_YAML.parent / "team" / "flatcheck.py"
GOLDEN = Path(__file__).resolve().parents[1] / "saves" / "golden"
AWAY = {"1h": 3600, "8h": 8 * 3600, "3d": 3 * 86_400}
"""How long after its last write an ended save is loaded under day one's rules."""


def route_json(p: DayOnePlayer) -> dict[str, dict[str, float | str]]:
    """flatcheck's --route: each landed id's game hours after the opening's end, and the visit it was seen in."""
    assert p.end_at is not None
    hours = {b: round((t - p.end_at) / 3600, 3) for b, t in p.landed_at.items()}
    visits: dict[str, float | str] = {}
    for b, t in p.seen_at.items():
        v = next((v for v in p.visits if v.start <= t <= v.end), None)
        visits[b] = f"V{v.index}" if v is not None else "away"
    return {"hours": dict(hours), "visits": visits}


def flatcheck(route: dict[str, dict[str, float | str]]) -> list[str]:
    """flatcheck.py's open flags for this route (accepted exceptions and its summary line left out)."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(route, f)
    out = subprocess.run([sys.executable, str(FLATCHECK), str(BEATS_YAML), "--route", f.name, "--days", "day_one"],
                         capture_output=True, text=True, check=False)
    Path(f.name).unlink()
    lines = [ln for ln in out.stdout.splitlines() if ln.strip() and not ln.startswith("beats=")]
    flags = [ln for ln in lines if not ln.endswith("[accepted]")]
    assert (out.returncode == 0) == (not flags), (out.returncode, out.stderr[-500:])
    return flags


# ---------- the rebase route ----------

@dataclass
class Rebased:
    """One ended golden save loaded into today's rules after `away`."""

    name: str
    at_load: Save
    load_lines: tuple[Line, ...]
    opened_at_load: list[str]
    landed_at: dict[str, int] = field(default_factory=lambda: {})
    opened_away: list[str] = field(default_factory=lambda: [])
    lines: list[Line] = field(default_factory=lambda: [])


def ended_saves() -> list[Path]:
    return sorted(p for p in GOLDEN.glob("f*/*.json") if "-end" in p.stem)


def rebased(path: Path, away: int, rules: Rules) -> Rebased:
    """Rebase at the save's own time (new content's triggers fire then), then the time away with nobody deciding,
    event by event."""
    old = path.read_text().strip()
    step = rebase_logged(old, rules, engine_renames(load_renames()))
    s = step.save
    r = Rebased(path.stem, s, step.lines, [])
    before = set(_manifest_triggers(old))
    r.opened_at_load = [t.id for t in one_per_moment(t for t, f in zip(rules.triggers, s.fired)
                                                     if f and t.id not in before and opens(rules, t.outcome.unlocks, s))]
    r.landed_at = {b: s.time for b in landed(s, rules)}
    r.opened_away = absence_unlocks(rules, s, away)
    end = s.time + away
    while s.time < end:
        e = next_event(s, rules)
        stepped = advance_logged(s, rules, end if e is None or e.time >= end else e.time)
        s = stepped.save
        r.lines += stepped.lines
        for b in landed(s, rules) - set(r.landed_at):
            r.landed_at[b] = s.time
    return r


def _manifest_triggers(text: str) -> list[str]:
    """The triggers the save's own rules declared, fired or not (its manifest): only the others can fire at the load
    as new content (engine DESIGN.txt, "Rebase", step 6)."""
    envelope: dict[str, dict[str, list[str]]] = json.loads(text)
    return [str(t) for t in envelope["manifest"]["triggers"]]


@cache
def rebased_case(path: Path, away: str) -> Rebased:
    """`rebased` under today's opening rules, kept for the session: the rebase tests and the readout read the same."""
    return rebased(path, AWAY[away], opening_rules())


def rebase_line(path: Path, away: str, r: Rebased) -> str:
    """The readout's line: what the load and the time away open."""
    return (f"  {path.parent.name}/{path.stem} {away:>3s}: the load opens {len(r.opened_at_load)} {r.opened_at_load}; "
            f"away {len(r.opened_away)} {r.opened_away}")


def rebase_problems(r: Rebased) -> list[str]:
    """The rebased story out of order."""
    found: list[str] = []
    order = sorted(r.landed_at, key=lambda b: (r.landed_at[b], STORY.index(b) if b in STORY else 99))
    story = [b for b in order if b in STORY]
    if story != [b for b in STORY if b in story] or story != list(STORY[:len(story)]):
        found.append(f"{r.name}: story out of order {story}")
    return found
