"""The pacing simulator's report and readouts for a played route past B4 (docs/design/day-three-plan.md, item 6): each
visit's counters beside day one's (new things, decisions, idle) and day three's two (spend, decide), the edge of written
content and returns during a long wait marked, per visit and per absence; when the beats from B5 land beside their
target days (daytwo/abs_band.py); and what the stores lose to their caps over the play and away from its last
decision. The readouts (NAMES) are committed under tests/readouts/ and compared by test_daythree_readouts.py; nothing
in them is a threshold. Day three's routes (routes.py) are read from the visit B4 is seen in. Minutes, hours and ids
only (CLAUDE.md, "Never spoil the owner").

    python -m tests.daythree.report typical     # from app/: the named routes through day three
    python -m tests.daythree.report typical --lines   # also each text key of day_three.toml with the states it
                                                      # showed or fired in
"""
import sys
import time

from tests.daythree import content as c3
from tests.daythree import counters, lines, verdicts, visits
from tests.daythree.routes import day3
from tests.daytwo import abs_band
from tests.daytwo import checks as checks2
from tests.daytwo.player import DayTwoPlayer, visit_seen
from tests.daytwo.routes import ROUTES
from tests.dayone import caploss, checks
from tests.dayone.player import DayOnePlayer
from tests.dayone.report import row

NAMES = ("daythree-typical", "daythree-sharp")


def absence_line(found: list[counters.Counts]) -> str:
    """Spend and decide summed over the visits that follow an absence of the length: under 2 h, 2 to 8 h, 8 h and over."""
    bands = {"<2h": (0, 2), "2-8h": (2, 8), "8h+": (8, 10**6)}
    parts = list[str]()
    for label, (lo, hi) in bands.items():
        inside = [c for c in found if lo <= c.gap / 3600 < hi]
        parts.append(f"{label}: {len(inside)} returns, spend {sum(c.spend for c in inside)}, "
                     f"decide {sum(c.decide for c in inside)}")
    return "  per absence  " + "; ".join(parts)


def mark(label: str, marked: dict[str, str]) -> str:
    return f"  [{marked[label]}]" if label in marked else ""


def cap_loss_lines(p: DayOnePlayer, start: int) -> list[str]:
    history = [s for s, _ in p.history if s.time >= start]
    tally = caploss.Tally()
    caploss.between(history, p.rules, tally)
    away = caploss.absences(history[-1], p.rules)
    return [f"  lost to caps: played {100 * caploss.total_share(tally.losses()):.0f}%, "
            + ", ".join(f"away {h} h {100 * caploss.total_share(away[h]):.0f}%" for h in caploss.ABSENCE_H)]


def beats_line(name: str, p: DayOnePlayer) -> str:
    pace = abs_band.load_pace()
    return "  " + abs_band.summary(name, abs_band.reached(p.landed_at, p.history[0][0].time, pace), pace)


def route_lines(name: str, p: DayOnePlayer, found: list[counters.Counts], first_visit: int,
                marked: dict[str, str]) -> list[str]:
    """The route's visits from `first_visit` (the first of the chapter) with their counts and marks."""
    assert p.end_at is not None
    mine = [w for w in checks.windows(p)][first_visit - 1:]
    out = [f"{name}: {len(mine)} visits from V{first_visit}"]
    out += [row(w, p) + "  |  " + counters.line(c) + mark(c.label, marked) for w, c in zip(mine, found)]
    return out + [absence_line(found), beats_line(name, p), *cap_loss_lines(p, mine[0].start)]


def first_visit(p: DayTwoPlayer) -> int:
    """The visit B4 is seen in: day three's V1."""
    return visit_seen(p.visits, p.seen_at.get("B4")) or 1


def typical_text(p: DayTwoPlayer, found: list[counters.Counts]) -> str:
    first = first_visit(p)
    return "\n".join(route_lines("typical", p, found, first, checks2.marks(p, verdicts.NOT_WAITS, first))) + "\n"


def sharp_text(p: DayTwoPlayer) -> str:
    return beats_line("sharp", p).strip() + "\n"


def readouts() -> dict[str, str]:
    p = day3("typical")
    return {"daythree-typical": typical_text(p, verdicts.chapter_counts(p)), "daythree-sharp": sharp_text(day3("sharp"))}


def main(argv: list[str]) -> int:
    plays = {name: day3(name) for name in argv if name in ROUTES}
    for name, p in plays.items():
        t0 = time.process_time()
        first = first_visit(p)
        found = [counters.count(v, p.rules) for v in visits.visits_of(p)][first - 1:]
        print("\n".join(route_lines(name, p, found, first, checks2.marks(p, verdicts.NOT_WAITS, first))))
        print(f"  ({time.process_time() - t0:.1f} CPU s)")
    if "--lines" in argv:
        first = {n: first_visit(p) for n, p in plays.items()}
        print("\n".join(lines.report(plays, lines.chapter_keys(lines.DAY_THREE), c3.opening3(), first,
                                    {n: p.landed_at["B4"] for n, p in plays.items()})))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
