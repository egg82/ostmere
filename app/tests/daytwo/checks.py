"""Day two's counters and checks on one played route (content/team/day-two.md, "Per visit", "Per absence"), each a
pure function of the player's records. Day two's visits run from the one B3 is seen in (its V1, measured from B3's
showing) to the one B4 is seen in; the readout prints each with day one's counters (tests/dayone/checks.py), marks
the visit at the edge of written content and each return during a long wait the player chose (long_waits), and lists
what each absence between two of them opens, counted between the saves the play itself passed through (no extra run).
The one check: a tool user's B4 no later than the babysitter's plus one of its day-two gaps for each step on B4's way
that waits for the player (bands.presence_steps, plus each offer on the way: an answer is a decision). Ids, hours and
visits only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Collection
from dataclasses import replace
from functools import cache

from ashfall_app.engine import LaneBar, Rules, Save, view
from ashfall_app.opening.schema import DAY_ONE, load_opening
from tests.daytwo.content import STORY, rules2
from tests.daytwo.player import DayTwoPlayer, visit_seen
from tests.dayone import checks
from tests.dayone.bands import presence_steps
from tests.dayone.human import thresholds
from tests.dayone.player import VisitRecord

B4_WAY = "build_shelter"
"""The card the offer's gate waits on: B4's way back runs through it, then the offer and the walk."""
OFFERS_ON_WAY = 1


def b3_at(p: DayTwoPlayer) -> int:
    assert "B3" in p.landed_at, "B3 never landed"
    return p.landed_at["B3"]


def b4_hours(p: DayTwoPlayer) -> float | None:
    """B4's landing, game hours after B3's."""
    return None if "B4" not in p.landed_at else round((p.landed_at["B4"] - b3_at(p)) / 3600, 2)


def day_visits(p: DayTwoPlayer) -> list[VisitRecord]:
    first = p.b3_visit()
    return [v for v in p.visits if first is not None and v.index >= first]


def windows(p: DayTwoPlayer) -> list[checks.Window]:
    """Day two's visits as day one's checks read them, labelled V1 on; V1 starts where B3 is seen."""
    first, seen = p.b3_visit(), p.seen_at.get("B3", 0)
    out: list[checks.Window] = []
    for w in checks.windows(p):
        n = int(w.label[1:])
        if first is None or n < first:
            continue
        if n == first:
            w = replace(w, start=seen, news=tuple(x for x in w.news if x.at >= seen),
                        acts=tuple(a for a in w.acts if a[0] >= seen))
        out.append(replace(w, label=f"V{n - first + 1}"))
    return out


def long_jobs(lanes: tuple[LaneBar, ...], now: int, gap_s: float) -> set[tuple[str, str]]:
    """(lane, card) of each tap, on any lane, landing beyond gap_s of now: a long job (the leave rule's dead gap,
    human.lands_within). Her lane counts: her walk is the player's answer."""
    return {(str(b.lane), str(b.card)) for b in lanes
            if b.card is not None and b.completes_at is not None and b.completes_at - now > gap_s}


def still_running(lanes: tuple[LaneBar, ...]) -> set[tuple[str, str]]:
    return {(str(b.lane), str(b.card)) for b in lanes if b.card is not None}


def waited_on(left: tuple[int, tuple[LaneBar, ...]], back: tuple[int, tuple[LaneBar, ...]], gap_s: float) -> bool:
    """A long job the player set going is running at the return: one left running at the exit (`left`: its time and
    lanes) and still running, or one landing beyond the dead gap of the return (`back`). The second is a job started
    while away, which only the player's own answers, queue and rules start: an answer's walk ordered behind her
    current tap, or an answer set ahead."""
    return bool(long_jobs(left[1], left[0], gap_s) & still_running(back[1]) or long_jobs(back[1], back[0], gap_s))


def long_waits(p: DayTwoPlayer, not_waits: Collection[str] = ()) -> dict[int, int]:
    """For each return during a long wait (waited_on): the return's time, and the lines logged from the exit before
    it to the visit's end. A card in `not_waits` is never the long job: work a chain needs rather than a wait chosen."""
    gap, back = thresholds().dead_gap_s(), returns(p)
    found: dict[int, int] = {}
    for a, b in zip(p.visits, p.visits[1:]):
        if a.exit is None or b.start not in back:
            continue
        left, at_return = jobs(a.exit, p.rules, not_waits), jobs(back[b.start], p.rules, not_waits)
        if waited_on((a.end, left), (b.start, at_return), gap):
            found[b.start] = sum(1 for ln in p.lines if a.end < ln.time <= b.end)
    return found


def jobs(save: Save, rules: Rules, not_waits: Collection[str]) -> tuple[LaneBar, ...]:
    return tuple(b for b in view(save, rules).lanes if str(b.card) not in not_waits)


def returns(p: DayTwoPlayer) -> dict[int, Save]:
    """The save at each visit's start (the return), read off the play's history."""
    starts = {v.start for v in p.visits}
    found: dict[int, Save] = {}
    for s, _ in p.history:
        if s.time in starts and s.time not in found:
            found[s.time] = s
    return found


def absences(p: DayTwoPlayer) -> list[tuple[str, list[str]]]:
    """(label, what opened) for each absence between two of day two's visits."""
    vs, back = day_visits(p), returns(p)
    out: list[tuple[str, list[str]]] = []
    for i, (a, b) in enumerate(zip(vs, vs[1:]), start=1):
        if a.exit is None or b.start not in back:
            continue
        out.append((f"V{i}->V{i + 1}", checks.unlocks_between(p.rules, a.exit, back[b.start])))
    return out


def story_order(landed_at: dict[str, int]) -> list[str]:
    """Day two's beats all land, in the authored order."""
    missing = [b for b in STORY if b not in landed_at]
    order = sorted((b for b in STORY if b in landed_at), key=lambda b: (landed_at[b], STORY.index(b)))
    found = [f"never landed: {missing}"] if missing else []
    return found + ([f"order {order}"] if order != [b for b in STORY if b in order] else [])


@cache
def day_one_ids() -> frozenset[str]:
    o = load_opening(chapters=(DAY_ONE,))
    return frozenset([*(c.id for c in o.cards), *(t.id for t in o.triggers)])


@cache
def b4_steps() -> int:
    """The steps on B4's way that wait for a return: the triggers that open a card on it (day one's content is where
    the walk stops), and the offer."""
    return len(presence_steps(rules2(), B4_WAY, day_one_ids())) + OFFERS_ON_WAY


def b4_relative(p: DayTwoPlayer, babysitter: DayTwoPlayer) -> list[str]:
    """B4 no later than the babysitter's plus the route's b4_steps largest day-two gaps."""
    hours, floor = b4_hours(p), b4_hours(babysitter)
    if hours is None or floor is None:
        return [f"B4 at {hours} h, babysitter's at {floor} h"]
    gaps = [v.gap / 3600 for v in day_visits(p)[1:]]
    bound = floor + sum(sorted(gaps, reverse=True)[:b4_steps()])
    return [] if hours <= bound + 1e-9 else [f"B4 at {hours} h, past the babysitter's {floor} h plus "
                                            f"{b4_steps()} gaps ({bound:.1f} h)"]


def marks(p: DayTwoPlayer, not_waits: Collection[str] = (), first: int | None = None) -> dict[str, str]:
    """By visit label: "edge" for the visit the route's last written beat is seen in, "wait, N lines" for a return
    during a long wait the player chose (long_waits, never on a card in `not_waits`) with the lines logged across it.
    Labels are day two's (V1 where B3 is seen), or the play's own from visit `first` on when it is given."""
    edge, waits = visit_seen(p.visits, p.seen_at.get(p.stop_beat())), long_waits(p, not_waits)
    labelled = list(zip(windows(p), day_visits(p))) if first is None else \
        [(w, v) for w, v in zip(checks.windows(p), p.visits) if v.index >= first]
    out: dict[str, str] = {}
    for w, v in labelled:
        if v.index == edge:
            out[w.label] = "edge"
        elif v.start in waits:
            out[w.label] = f"wait, {waits[v.start]} lines"
    return out
