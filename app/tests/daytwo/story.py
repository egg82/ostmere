"""Day two's story shape on a played route, checked by the content team's flatcheck.py (both day lists) fed the
route: each day-two id's game hours after B3 and the day-two visit it was seen in, and each day-two beat's day of play
for the spine's week checks; day one's ids keep their authored hours (day one's own simulator feeds those). Ids,
hours and visits only."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.daytwo.checks import b3_at, day_visits
from tests.daytwo.content import DAY_TWO_IDS, OFFERS, STORY
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.beats import BEATS_YAML
from tests.dayone.schedules import HOUR, OPENING_CLOCK
from tests.dayone.story import FLATCHECK

DAY_S = 24 * HOUR
DAYS = "day_one,day_two"
"""Both day lists, so the spine's week and run checks see day one's beats between B2 and B3 as they stand."""


def play_day(t: int) -> int:
    """The day of play (1 = the day the opening is started, at OPENING_CLOCK on the player's clock)."""
    return 1 + (OPENING_CLOCK + t) // DAY_S


def route_json2(p: DayTwoPlayer) -> dict[str, object]:
    """B3 is left to each day list's own target_hour: day one counts its hours from the opening's end, day two from B3,
    and the route file has one "hours" table for both."""
    b3, vs = b3_at(p), day_visits(p)
    ids = (*DAY_TWO_IDS, *(b for b in STORY if b != "B3"))
    hours = {b: round((p.landed_at[b] - b3) / 3600, 3) for b in ids if b in p.landed_at}
    visits: dict[str, str] = {}
    for b in hours:
        t = p.seen_at.get(b)
        n = next((i for i, v in enumerate(vs, start=1) if t is not None and v.start <= t <= v.end), None)
        visits[b] = "away" if n is None else f"V{n}"
    days = {b: play_day(p.landed_at[b]) for b in (*STORY, *OFFERS) if b in p.landed_at}
    return {**days, "hours": hours, "visits": visits}


def flatcheck2(p: DayTwoPlayer) -> list[str]:
    """flatcheck.py's open flags for day two on this route (accepted ones and its summary line left out)."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(route_json2(p), f)
    out = subprocess.run([sys.executable, str(FLATCHECK), str(BEATS_YAML), "--route", f.name, "--days", DAYS],
                         capture_output=True, text=True, check=False)
    Path(f.name).unlink()
    lines = [ln for ln in out.stdout.splitlines() if ln.strip() and not ln.startswith("beats=")]
    flags = [ln for ln in lines if not ln.endswith("[accepted]")]
    assert (out.returncode == 0) == (not flags), (out.returncode, out.stderr[-500:])
    return flags
