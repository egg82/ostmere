"""When each spine beat from B5 on lands, for the readouts: its day from the save's start beside the beat's target_day
and the pace_scale, both read off content/beats.yaml (the one place). Information, never a band
(docs/design/sim-invariants.md). Ids and days only (CLAUDE.md, "Never spoil the owner")."""
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tests.dayone.beats import BEATS_YAML

FIRST = 5
"""The first spine beat the readout lists by day: B4 is read in hours after B3 (daytwo/checks.py, b4_hours)."""
DAY_S = 24 * 3600
NONE_REACHED = "no beat from B5 reached"


@dataclass(frozen=True)
class Pace:
    scale: float
    targets: Mapping[str, int]
    """Target day per spine beat id, B5 on."""


def load_pace(path: Path = BEATS_YAML) -> Pace:
    text = path.read_text()
    found = re.search(r"^pace_scale:\s*([\d.]+)", text, re.M)
    assert found is not None, "beats.yaml names no pace_scale"
    section = text.split("\nbeats:\n", 1)[1].split("\n\n", 1)[0] if "\nbeats:\n" in text else ""
    targets = {m.group(1): int(m.group(2)) for m in re.finditer(r"\{id:\s*(B\d+),[^\n]*?target_day:\s*(\d+)", section)
               if int(m.group(1)[1:]) >= FIRST}
    scale = float(found.group(1))
    assert scale > 0 and targets, "read no pace_scale or no target day from B5 on"
    return Pace(scale, targets)


def reached(landed_at: Mapping[str, int], start: int, pace: Pace) -> dict[str, float]:
    """The days from the save's start of each beat from B5 on that the route reached."""
    return {b: round((t - start) / DAY_S, 2) for b, t in sorted(landed_at.items()) if b in pace.targets}


def summary(route: str, days: Mapping[str, float], pace: Pace) -> str:
    """The readout's line: each beat the route reached, its day beside its target_day, or that it reached none."""
    if not days:
        return f"beats {route}: {NONE_REACHED} (pace_scale {pace.scale:g})"
    return (f"beats {route} (pace_scale {pace.scale:g}): "
            + ", ".join(f"{b} day {d:g}, target_day {pace.targets[b]}" for b, d in days.items()))
