"""Something to build toward, and promises kept (docs/decisions.md), on a played route, read off the saves the player
saw from the opening's end until B3 is seen (day one's span), at most one sample per SAMPLE_S, plus each visit's exit
in that span; never while the hands run a tap, which holds the mix for its few seconds.

Goals, a readout (report.py). A goal is a skill row's next level whose marker the row shows (a pays entry above the
level). It is driven by the setup when a one-card mix of the hands card that trains it reaches that level sooner than
a one-card mix of another hands card open then, both run on the real engine from that save; the camp bar fills from
any hands work, so no setup drives it, and a timer (the night) is never a goal. Weighting decides the order when, for
some pair of driven goals both at least CHOICE_S out under their good setup, a 75/25 mix each way reaches a different
one first. `goal_summary` counts both over the samples.

Promises. Sampled through day one and on past its end card (AFTER_CARD_S of the play after B3 is seen, then the last
visit's exit with nobody deciding), since nothing past the card may be drawn as a wait that will pay. What the page
draws as a time must come true by itself: advanced from the sample with nobody deciding to that time, the card is ready or done, the store holds its cap or is empty, the level has landed. A card's countdown is
drawn under game/ready.ts's rule; a "full in", an "empty in" and a skill row's time come from the forecast (api
CONTRACT.txt, "Forecast"), the first it lists after now, as the page draws them. Problems name minutes and ids only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from itertools import combinations

from ashfall_app.api.service import FORECAST_S
from ashfall_app.engine import (
    BP, HANDS, AtLeast, AtMost, CardId, CardShare, Forecast, InvalidVerbError, Mix, MixId, Rules, Save, SaveMix,
    StoreId, StoreValue, SwitchMix, UnlockKind, View, advance, decide, forecast, view,
)
from tests.dayone.player import DayOnePlayer
from tests.opening.playthrough import opening

SAMPLE_S = 600
CHOICE_S = 600
"""Design choice (docs/decisions.md): a goal counts toward the weighting pair, and toward a choice being due, only
when the good setup reaches it at least this far out: a goal minutes away is not a choice, one ten minutes out is."""
PROBE = MixId("goal probe")
AFTER_CARD_S = 24 * 3600
AFTER_EVERY_S = 3 * 3600
"""Past day one's end card, the promise samples run this long, at most one each AFTER_EVERY_S."""


@dataclass(frozen=True)
class Goal:
    skill: str
    level: int
    card: str
    """The hands card that trains the skill."""


@cache
def pays() -> dict[str, frozenset[int]]:
    """Each skill's levels that carry a marker (a pays entry), as the page's catalog has them."""
    return {s.id: frozenset(lv.level for lv in s.levels) for s in opening().skills}


def samples(p: DayOnePlayer) -> Iterator[tuple[Save, View]]:
    """The saves the player saw from the end until B3 is seen, at most one per SAMPLE_S, then each visit's exit."""
    assert p.end_at is not None
    stop = p.seen_at.get("B3", p.save.time)
    last = None
    for save, v in p.history:
        tapping = any(b.lane == HANDS and b.card is not None for b in v.lanes)   # a tap holds the mix: no setup now
        if p.end_at <= save.time <= stop and not tapping and (last is None or save.time - last >= SAMPLE_S):
            last = save.time
            yield save, v
    for visit in p.visits:
        if visit.exit is not None and visit.exit.time != last and visit.exit.time <= stop:
            yield visit.exit, view(visit.exit, p.rules)


def trainers(rules: Rules) -> dict[str, tuple[str, ...]]:
    """Each skill's hands cards that train it, in the rules' order (a later chapter adds more than one)."""
    out: dict[str, tuple[str, ...]] = {}
    for c in rules.cards:
        if c.lane == HANDS and c.skill is not None:
            out[str(c.skill)] = (*out.get(str(c.skill), ()), str(c.id))
    return out


def open_goals(save: Save, v: View, rules: Rules) -> list[Goal]:
    shown = {u.id for u in save.unlocked if u.kind is UnlockKind.SKILL}
    cards = {str(u.id) for u in save.unlocked if u.kind is UnlockKind.CARD}
    feed = trainers(rules)
    out: list[Goal] = []
    for bar in v.skills:
        nxt = min((lv for lv in pays().get(bar.skill, frozenset()) if lv > bar.level), default=None)
        card = next((c for c in feed.get(bar.skill, ()) if c in cards), None)
        if bar.skill in shown and nxt is not None and card is not None:
            out.append(Goal(bar.skill, nxt, card))
    return out


def etas(save: Save, rules: Rules, shares: tuple[tuple[str, int], ...]) -> dict[str, int | None] | None:
    """Each skill's next level time with this mix running (None for the mix when it cannot be saved now)."""
    try:
        s = decide(save, rules, save.time, SaveMix(Mix(PROBE, tuple(CardShare(CardId(c), bp) for c, bp in shares))))
        s = decide(s, rules, save.time, SwitchMix(PROBE))
    except InvalidVerbError:
        return None
    return {b.skill: b.next_level_at for b in view(s, rules).skills}


def driven(save: Save, rules: Rules, goal: Goal, others: list[str]) -> bool:
    good = etas(save, rules, ((goal.card, BP),))
    at = None if good is None else good.get(goal.skill)
    if at is None:
        return False
    for other in others:
        poor = etas(save, rules, ((other, BP),))
        slow = None if poor is None else poor.get(goal.skill)
        if poor is not None and (slow is None or at < slow):
            return True
    return not others


def far_out(save: Save, rules: Rules, goals: list[Goal]) -> list[Goal]:
    """The goals the good setup (a one-card mix of the goal's own card) reaches at least CHOICE_S out."""
    out: list[Goal] = []
    for g in goals:
        good = etas(save, rules, ((g.card, BP),))
        at = None if good is None else good.get(g.skill)
        if at is not None and at - save.time >= CHOICE_S:
            out.append(g)
    return out


def weighting_decides(save: Save, rules: Rules, goals: list[Goal]) -> bool | None:
    """True when two 75/25 mixes reach different goals first; None when no pair is both driven and CHOICE_S out."""
    far = far_out(save, rules, goals)
    pairs = 0
    for x, y in combinations(far, 2):
        a = etas(save, rules, ((x.card, 7500), (y.card, 2500)))
        b = etas(save, rules, ((y.card, 7500), (x.card, 2500)))
        ax, ay = (None, None) if a is None else (a.get(x.skill), a.get(y.skill))
        bx, by = (None, None) if b is None else (b.get(x.skill), b.get(y.skill))
        if ax is None or ay is None or bx is None or by is None:
            continue
        pairs += 1
        if (ax < ay) != (bx < by):
            return True
    return False if pairs else None


@dataclass(frozen=True)
class GoalSample:
    at_min: float
    goals: tuple[str, ...]
    """Each open goal as skill->level, with '*' when the setup drives it."""
    weighting: bool | None
    choice_due: bool = True
    """False when no open goal is CHOICE_S out under the good setup: neither pass nor fail, reported."""


def goal_samples(p: DayOnePlayer) -> list[GoalSample]:
    assert p.end_at is not None
    out: list[GoalSample] = []
    for save, v in samples(p):
        goals = open_goals(save, v, p.rules)
        hands = [g.card for g in goals]
        marks = [driven(save, p.rules, g, [c for c in hands if c != g.card] or _other(p.rules, save, g.card))
                 for g in goals]
        on = [g for g, m in zip(goals, marks) if m]
        out.append(GoalSample(round((save.time - p.end_at) / 60, 1),
                              tuple(f"{g.skill}->{g.level}{'*' if m else ''}" for g, m in zip(goals, marks)),
                              weighting_decides(save, p.rules, on), bool(far_out(save, p.rules, goals))))
    return out


def _other(rules: Rules, save: Save, card: str) -> list[str]:
    """Hands cards open now besides `card`, for a goal alone on the screen."""
    cards = {str(u.id) for u in save.unlocked if u.kind is UnlockKind.CARD}
    return [str(c.id) for c in rules.cards if c.lane == HANDS and str(c.id) in cards and c.cap is None
            and str(c.id) != card][:1]


@dataclass(frozen=True)
class GoalSummary:
    """The goal samples as the readout counts them."""

    samples: int
    choice_due: int
    undriven: int
    """Samples with a choice due and no goal the setup drives."""
    judged: int
    """Samples with a pair of driven goals both CHOICE_S out."""
    decided: int
    """... of which a 75/25 mix each way reaches a different one first."""


def goal_summary(found: list[GoalSample]) -> GoalSummary:
    judged = [s.weighting for s in found if s.weighting is not None]
    return GoalSummary(len(found), sum(1 for s in found if s.choice_due),
                       sum(1 for s in found if s.choice_due and not any(g.endswith("*") for g in s.goals)),
                       len(judged), sum(judged))


# ---------- promises ----------

def stops_short(save: Save, store: str, need: int) -> bool:
    """game/ready.ts: an under-x-until-y rule on the store that is on lets go below the need."""
    watched = StoreValue(StoreId(store))
    return any(on and isinstance(o.when, AtMost) and o.when.subject == watched and o.when.release + 1 < need
               for o, on in zip(save.orders, save.latches))


def page_forecast(save: Save, rules: Rules) -> Forecast:
    """The forecast the API serves with this save's view (api/service.py)."""
    shown = tuple(StoreId(u.id) for u in save.unlocked if u.kind is UnlockKind.STORE)
    return forecast(save, rules, save.time + FORECAST_S, shown)


def drawn(save: Save, v: View, rules: Rules) -> list[tuple[str, str, int]]:
    """(kind, id, time) for every time the page draws: card countdowns, a ledger line's "full in" or "empty in", a
    skill row's next level, each the first the forecast lists after now (game/forecast.ts). The Camp store has no ledger
    line (ui/ledger.ts draws it as the Camp bar, which shows no time), so no fill or emptying of it is drawn."""
    out: list[tuple[str, str, int]] = []
    f = page_forecast(save, rules)
    for c in v.cards:
        b = c.blocker
        if b is None or b.ready_at is None:
            continue
        w = b.condition
        if isinstance(w, AtLeast) and isinstance(w.subject, StoreValue) and stops_short(save, w.subject.store, w.value):
            continue
        at = full_ready_at(v, f, w, b.ready_at) if isinstance(w, AtLeast) else b.ready_at
        if at is not None:
            out.append(("card", c.card, at))
    camp = opening().camp
    lines = [ln for ln in v.ledger if camp is None or ln.store != camp.store]
    rising = {ln.store for ln in lines if ln.net_per_hour > 0}
    falling = {ln.store for ln in lines if ln.falling}
    out += [("full", st, at) for st, ts in f.fills.items() if st in rising if (at := _first(ts, save.time))]
    out += [("empty", st, at) for st, ts in f.empties.items() if st in falling if (at := _first(ts, save.time))]
    out += [("level", sk, at) for sk, ts in f.level_ups.items()
            if any(lv > _level(v, sk) for lv in pays().get(sk, frozenset())) if (at := _first(ts, save.time))]
    return out


def full_ready_at(v: View, f: Forecast, w: AtLeast, ready_at: int) -> int | None:
    """game/ready.ts: a card waiting on its store's whole cap is drawn at the forecast's fill (None past its horizon);
    any other wait at the blocker's ready_at."""
    if not isinstance(w.subject, StoreValue):
        return ready_at
    store = w.subject.store
    line = next((ln for ln in v.ledger if ln.store == store), None)
    return ready_at if line is None or w.value < line.cap else _first(f.fills.get(store, ()), v.time)


def _first(times: tuple[int, ...], now: int) -> int | None:
    return next((t for t in times if t > now), None)


def _level(v: View, skill: str) -> int:
    return next(b.level for b in v.skills if b.skill == skill)


def kept(save: Save, rules: Rules, v: View, kind: str, ident: str, at: int) -> bool:
    later = view(advance(save, rules, at), rules)
    if kind == "card":
        c = next((x for x in later.cards if x.card == ident), None)
        return c is None or c.blocker is None
    if kind in ("full", "empty"):
        after = next(x for x in later.ledger if x.store == ident)
        return after.segment.start_value >= after.cap if kind == "full" else after.segment.start_value == 0
    level = next(b.level for b in v.skills if b.skill == ident)
    return next(b.level for b in later.skills if b.skill == ident) > level


def after_card(p: DayOnePlayer) -> Iterator[tuple[Save, View]]:
    """The saves past B3 being seen (the end card follows it): the play's own, then its last save advanced with nobody
    deciding, at most one per AFTER_EVERY_S, to AFTER_CARD_S after it."""
    seen = p.seen_at["B3"]
    last = seen
    for save, v in p.history:
        if seen < save.time <= seen + AFTER_CARD_S and save.time - last >= AFTER_EVERY_S:
            last = save.time
            yield save, v
    for at in range(last + AFTER_EVERY_S, seen + AFTER_CARD_S + 1, AFTER_EVERY_S):
        if at > p.save.time:
            s = advance(p.save, p.rules, at)
            yield s, view(s, p.rules)


def promise_problems(p: DayOnePlayer) -> list[str]:
    assert p.end_at is not None
    out: list[str] = []
    later = list(after_card(p))
    assert later, "no sample past the end card"
    for save, v in [*samples(p), *later]:
        for kind, ident, at in drawn(save, v, p.rules):
            if not kept(save, p.rules, v, kind, ident, at):
                out.append(f"{kind} {ident} drawn at {(save.time - p.end_at) / 60:.0f}m for "
                           f"{(at - save.time) / 60:.0f}m later, not kept")
    return out
