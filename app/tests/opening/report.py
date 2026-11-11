"""The opening's readout (docs/design/sim-invariants.md): how its push routes move, printed and never judged. Per
route, the end moment and the longest run of taps of one card; the typical route's timeline of effort between new
things; what a day away opens from the first order; how the two crafts first show; each skill's climb against the
fastest; and the by_hand player's steps past the end. Minutes, counts and ids only (CLAUDE.md, "Never spoil the owner").

    python -m tests.opening.report     # from app/: print it
"""
import sys
from collections.abc import Mapping
from itertools import groupby

from ashfall_app.engine import Rules, advance_logged
from tests.dayone.growth import climb_hours
from tests.opening.afterend import AfterEnd
from tests.opening.playthrough import CRAFTS, News, Player, opening_rules
from tests.opening.routes import PUSH_ROUTES, after_end, route

NAMES = ("opening",)
DAY_S = 24 * 3600


def timeline(news: list[News]) -> list[tuple[int, list[str], int, int]]:
    """New things grouped by the moment they showed: (time, things, taps since the last, decisions since the last)."""
    rows: list[tuple[int, list[str], int, int]] = []
    last = (0, 0)
    for at, group in groupby(news, key=lambda n: n.at):
        items = list(group)
        taps, decisions = items[-1].taps, items[-1].decisions
        rows.append((at, [n.thing for n in items], taps - last[0], decisions - last[1]))
        last = (taps, decisions)
    return rows


def longest_run(p: Player) -> tuple[str, int]:
    runs = [(card, len(list(g))) for card, g in groupby(p.taps())]
    return max(runs, key=lambda r: r[1], default=("", 0))


def day_away(typical: Player) -> list[str]:
    """The triggers that open something in a day with no decisions from the first order."""
    p = typical.at(lambda q: bool(q.save.orders))
    away = advance_logged(p.save, p.rules, p.save.time + DAY_S).save
    return sorted(str(t.id) for i, t in enumerate(p.rules.triggers)
                  if away.fired[i] and not p.save.fired[i] and t.outcome.unlocks)


def crafts_shown(typical: Player) -> str:
    p = typical.at(lambda q: q.card(CRAFTS[0]) is not None)
    return ", ".join(f"{c} {'absent' if (v := p.card(c)) is None else 'blocked' if v.blocker else 'ready'}" for c in CRAFTS)


def climb_lines(rules: Rules) -> list[str]:
    hours = climb_hours(rules)
    best = min(hours.values())
    return [f"  {skill:14s} {h:6.0f} h to the curve's top, x{h / best:.2f} the fastest" for skill, h in sorted(hours.items())]


def after_end_line(a: AfterEnd) -> str:
    def mm(t: int | None) -> str:
        return "never" if t is None else f"{t / 60:.1f}m"

    def gap(x: int | None, y: int | None) -> int | None:
        return None if x is None or y is None else x - y

    effort = gap(a.effort_at.get("door"), a.effort_at.get("offer"))
    return (f"  by_hand past the end: read -> offer {mm(gap(a.offer_at, a.read_at))}; offer -> accepted "
            f"{mm(gap(a.accepted_at, a.offer_at))}; read -> door {mm(gap(a.door_at, a.read_at))}; actions between "
            f"offer and door {effort}")


def render(routes: Mapping[str, Player], a: AfterEnd) -> str:
    out = ["routes"]
    for name, p in routes.items():
        card, n = longest_run(p)
        out.append(f"  {name:15s} end {(p.end_at or 0) / 60:5.1f}m  longest run {n} of {card}")
    out.append("typical timeline: time, taps and decisions since the last new thing, how many new things")
    out += [f"  {at // 60:3d}:{at % 60:02d}  +{t}T +{d}D  {len(things)}"
            for at, things, t, d in timeline(routes["typical"].news)]
    out.append(f"a day away from the first order opens: {day_away(routes['typical'])}")
    out.append(f"the crafts at first show: {crafts_shown(routes['typical'])}")
    out.append("each skill's climb at a full share of its fastest runner")
    out += climb_lines(opening_rules())
    out.append(after_end_line(a))
    return "\n".join(out) + "\n"


def readouts() -> dict[str, str]:
    return {"opening": render({name: route(name) for name in PUSH_ROUTES}, after_end("by_hand")[0])}


if __name__ == "__main__":
    print(readouts()["opening"], end="")
    sys.exit(0)
