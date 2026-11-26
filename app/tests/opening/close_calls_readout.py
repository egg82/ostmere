"""The close calls' readout: per notable, each close call by id with the spine beat it lands with, that beat's story day,
the real days of play at the typical route's pace (target_day x pace_scale, content/beats.yaml), the days since their
previous one, and the change that followed ("NO CHANGE" when the entry names none). Taste, so it reports and fails
nothing (docs/design/sim-invariants.md): how many is too many, and how far apart, are judged by reading it. Ids and
numbers only (CLAUDE.md, "Never spoil the owner").

    python -m tests.opening.close_calls_readout     # from app/: print it
"""
import sys

from ashfall_app.opening.schema import Opening, load_opening
from tests.daytwo.abs_band import Pace, load_pace

NAMES = ("closecalls",)
NONE_MARKED = "no content marks a close call yet"


def render(o: Opening, pace: Pace) -> str:
    notables = [x.id for x in o.lanes if x.notable]
    if not notables:
        return "no notable is marked yet"
    if not o.close_calls:
        return f"{len(notables)} notables: {NONE_MARKED}"
    lines = ["notable  close call  beat  story day  real days  since previous  change"]
    for lane in notables:
        calls = sorted((c for c in o.close_calls if c.person == lane), key=lambda c: (_real(c.beat, pace) or 0, c.id))
        lines.append(f"{lane}: {len(calls)} close calls")
        previous: float | None = None
        for c in calls:
            real = _real(c.beat, pace)
            since = "-" if previous is None or real is None else f"{real - previous:g}"
            day = pace.targets.get(c.beat)
            lines.append(f"  {c.id}  {c.beat}  {day if day is not None else 'unknown'}  "
                         f"{f'{real:g}' if real is not None else 'unknown'}  {since}  {c.change or 'NO CHANGE'}")
            previous = real if real is not None else previous
    return "\n".join(lines)


def _real(beat: str, pace: Pace) -> float | None:
    day = pace.targets.get(beat)
    return None if day is None else day * pace.scale


def readouts() -> dict[str, str]:
    return {"closecalls": render(load_opening(), load_pace())}


if __name__ == "__main__":
    print(readouts()["closecalls"])
    sys.exit(0)
