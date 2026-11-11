"""The worth readout: what a re-mix is worth, visit by visit, on the typical route through the edge of written content
(docs/design/worth-a-change.md, "What the simulator measures"; the routes: tests/worth/route.py, the measure:
tests/worth/probe.py). Per day: keeper's worth at its visits, tuner's moments and their causes; then each route's worth
by decile (the two controls among them), fresh's worth with and without a cause (what the threshold is read from), how
far the kept rates came true, the opening's moments per visit beside each week's, the longest stretch with none, and
every visit. It reports and fails nothing; its text is committed under tests/readouts/ and compared by
tests/weektwo/test_worth_readouts.py, whose job has day fifteen's plays. Goals are skill ids and levels, causes are kinds (CLAUDE.md, "Never spoil the owner").

    python -m tests.worth.readout            # from app/: print the readout and its CPU cost
"""
import sys
import time
from collections import Counter
from collections.abc import Callable

from tests.dayone.player import DayOnePlayer
from tests.weektwo.routes import fifteen
from tests.worth import summary as sm
from tests.worth.route import visit_worths

ROUTE = "typical"
NAMES = (f"worth-{ROUTE}",)
Pick = Callable[[sm.VisitWorth], float | None]
ROUTES: tuple[tuple[str, Pick], ...] = (
    ("keeper", lambda v: v.keeper_s),
    ("tuner", lambda v: v.tuner_s),
    ("fresh (control: little)", lambda v: v.fresh_s),
    ("once (control: a lot)", lambda v: v.once_s),
)


def worths(visits: list[sm.VisitWorth], pick: Pick) -> list[float]:
    return [sm.fraction(v.best_s, pick(v)) for v in visits if v.best_s is not None]


def decile_line(name: str, values: list[float]) -> str:
    return f"    {name:26s} n={len(values):2d}: " + " ".join(f"{x * 100:.0f}" for x in sm.deciles(values))


def day_rows(visits: list[sm.VisitWorth]) -> list[str]:
    """One line per game day: each visit's keeper worth, then tuner's moments with their causes."""
    out: list[str] = []
    for day in sorted({sm.day_of(v.at) for v in visits}):
        inside = [v for v in visits if sm.day_of(v.at) == day]
        keeper = "  ".join(sm.worth_cell(v.best_s, v.keeper_s) for v in inside)
        moments = [v for v in inside if v.moment]
        why = Counter(c for v in moments for c in v.causes or ("none found",))
        out.append(f"  day {day:2d}  visits {len(inside)}  keeper: {keeper}")
        out.append(f"          tuner moments {len(moments)}" +
                   (": " + ", ".join(f"{c} {n}" for c, n in sorted(why.items())) if moments else ""))
    return out


def visit_rows(visits: list[sm.VisitWorth]) -> list[str]:
    head = "  visit   day  goals  best    keeper       tuner        fresh        once         came  causes"
    return [head, *(f"  V{v.index:<4d}{v.at / sm.DAY_S:6.2f}  {v.goals:4d}  "
                    f"{'-' if v.best_s is None else f'{v.best_s / 3600:.1f}h':>6s}  "
                    + "".join(f"{sm.worth_cell(v.best_s, pick(v)):13s}" for _, pick in ROUTES)
                    + f"{'-' if v.came is None else f'{v.came:.2f}':>5s}  {'*' if v.moment else ' '}{','.join(v.causes)}"
                    for v in visits)]


def text(p: DayOnePlayer) -> str:
    visits = visit_worths(p)
    assert p.end_at is not None and any(v.goals for v in visits), "no visit with a goal to read"
    spans = sm.spans(visits, p.seen_at["B3"])
    ref = spans[0].rate
    dry = sm.longest_dry(visits, p.end_at, p.save.time)
    fresh = ROUTES[2][1]
    return "\n".join([
        f"== worth on {ROUTE}: {len(visits)} visits to the edge at game day {p.save.time / sm.DAY_S:.2f}",
        "  worth: how much later a route's mix lands the last of the set (the open goals that are a choice on skills the",
        "  player's mix trains) than the best setup, in hours and as a share of the route's time; never: a goal unserved",
        *day_rows(visits),
        f"  worth by route, percent by decile (threshold {sm.THRESHOLD * 100:.0f}%)",
        *(decile_line(name, worths(visits, pick)) for name, pick in ROUTES),
        "  fresh's worth by cause, percent by decile",
        decile_line("no cause", worths([v for v in visits if not v.causes], fresh)),
        decile_line("a cause", worths([v for v in visits if v.causes], fresh)),
        "  kept rates come true over the absence after (XP gained / XP the rates promised), by decile",
        "    " + " ".join(f"{x:.2f}" for x in sm.deciles([v.came for v in visits if v.came is not None])),
        "  moments per visit (opening = to B3 seen)",
        *(f"    {s.label:8s} {s.moments:2d} of {s.visits:2d} = {s.rate:.2f}   opening {ref:.2f}" for s in spans),
        f"  longest stretch with no moment: day {dry[0] / sm.DAY_S:.2f} to {dry[1] / sm.DAY_S:.2f} "
        f"({(dry[1] - dry[0]) / sm.DAY_S:.2f} d)",
        "  per visit (* tuner takes the best setup)",
        *visit_rows(visits),
    ]) + "\n"


def readouts() -> dict[str, str]:
    return {f"worth-{ROUTE}": text(fifteen(ROUTE))}


def main(argv: list[str]) -> int:
    t0 = time.process_time()
    p = fifteen(ROUTE)
    t1 = time.process_time()
    sys.stdout.write(text(p))
    print(f"(played in {t1 - t0:.0f} CPU s, read in {time.process_time() - t1:.1f} CPU s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
