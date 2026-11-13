"""The 2 AM test on day one (docs/decisions.md, "Fun, but never vying for attention"): a babysitter who acts the moment
every timer ends ends no further ahead than the whenever player who uses the queue and the rules, given the same
reveals.

"Given the same reveals" is made exact by replay. The whenever player's decisions after the opening are replayed on
its end-moment save twice, event by event to a common time: once as they were (W), and once as a babysitter (B) that
drops the queue and the rising-line rule and instead taps each of day one's rate- and cap-raising steps (BOOSTS) and
each smoke the rule would, at the very second it can while the whenever player is away; a step that player tapped
by hand while there, the babysitter taps at that player's own glance, since reaction time is not attention (both are
present then). Everything else (the steps that reveal, mix edits) happens at
the whenever player's own times in both. So any difference is attention earning something: a step the queue could not
wait on, a rule that could not cover a verb, or a step that was shown only while the player was away.

Measured on both: every store and skill XP at the common time, when each push of each boost step landed, and what
each store lost at its cap (its net while full, integrated)."""
from dataclasses import dataclass, field
from math import floor
from multiprocessing import get_context

from ashfall_app.engine import (
    AtLeast, CardId, InvalidVerbError, Rules, Save, SetOrders, SetQueue, TapCard, Verb, advance, decide, next_event,
)
from ashfall_app.engine.gates import store_cap
from ashfall_app.engine.rates import exact_net, running
from ashfall_app.engine.work import blocker, completions, tappable
from tests.dayone import policy

BOOSTS = policy.QUEUEABLE
SMOKE = CardId(policy.SMOKE)


@dataclass
class Measured:
    save: Save
    landed: dict[str, int] = field(default_factory=lambda: {})
    """"card#n": when the nth completion of a boost step landed."""
    waste: dict[str, int] = field(default_factory=lambda: {})
    """Store: quantity units lost at its cap."""


def babysat(log: list[tuple[int, Verb]]) -> list[tuple[int, Verb]]:
    """The whenever player's log without the queue and the rising-line rule: the babysitter does their work by hand."""
    out: list[tuple[int, Verb]] = []
    for t, verb in log:
        if isinstance(verb, SetQueue):
            continue
        if isinstance(verb, SetOrders):
            verb = SetOrders(tuple(o for o in verb.orders if not (isinstance(o.when, AtLeast) and o.then == TapCard(SMOKE))))
        out.append((t, verb))
    return out


@dataclass(frozen=True)
class Present:
    """The whenever player's visits, (start, end), and what it did by hand in them: each card tapped, and each card a
    rule it set taps, at the time it first set that rule (re-setting its orders later starts nothing new), and each
    card it queued, at the time it first queued it."""

    windows: tuple[tuple[int, int], ...]
    steps: tuple[tuple[int, CardId], ...]

    @classmethod
    def of(cls, windows: tuple[tuple[int, int], ...], log: list[tuple[int, Verb]]) -> "Present":
        steps: list[tuple[int, CardId]] = []
        ruled: set[CardId] = set()
        queued: set[CardId] = set()
        for t, v in log:
            if isinstance(v, TapCard):
                steps.append((t, v.card))
            elif isinstance(v, SetOrders):
                now = {o.then.card for o in v.orders if isinstance(o.then, TapCard)}
                steps += [(t, c) for c in sorted(now - ruled)]
                ruled = now
            elif isinstance(v, SetQueue):
                now = {e.verb.card for e in v.entries if isinstance(e.verb, TapCard)}
                steps += [(t, c) for c in sorted(now - queued)]
                queued = now
        return cls(windows, tuple(steps))


def replay(rules: Rules, start: Save, log: list[tuple[int, Verb]], until: int, babysit: bool,
           present: Present | None = None, boosts: tuple[str, ...] = BOOSTS) -> Measured:
    """`log` applied at its times from `start`, event by event to `until`; a verb that no longer fits is skipped (the
    babysitter already did it). `present`: a step the whenever player tapped, or set a rule to tap, while there the
    babysitter taps at that player's time too (the same glance), not the instant it turned ready. `boosts`: the
    rate- and cap-raising steps the babysitter taps and the measure times (day one's by default)."""
    m = Measured(start)
    s, i = start, 0
    while True:
        while i < len(log) and log[i][0] <= s.time:
            s, i = _try(s, rules, log[i][1]), i + 1
        if babysit:
            s = _babysit(s, rules, _glanced(s.time, present), boosts)
        _note(m, s, rules, boosts)
        if s.time >= until:
            m.save = s
            return m
        t = min(x for x in (until, log[i][0] if i < len(log) else None, _next(s, rules, babysit, boosts))
                if x is not None)
        _waste(m, s, rules, t - s.time)
        s = advance(s, rules, t)


def replay_pair(rules: Rules, start: Save, log: list[tuple[int, Verb]], until: int, present: Present,
                boosts: tuple[str, ...] = BOOSTS) -> tuple[Measured, Measured]:
    """(W, B): `log` replayed as it was and as a babysitter, the babysitter's in a child process while this one plays
    the whenever player's. The two share nothing past the first few game hours, so this halves the wall clock of a
    long chapter's pair on a machine with a core to spare."""
    with get_context("spawn").Pool(1) as pool:   # leaving it terminates the child, so a timeout here is not held up
        b = pool.apply_async(replay, (rules, start, babysat(log), until, True, present, boosts))
        return replay(rules, start, log, until, False, boosts=boosts), b.get()


def _try(s: Save, rules: Rules, verb: Verb) -> Save:
    try:
        return decide(s, rules, s.time, verb)
    except InvalidVerbError:
        return s


def _glanced(now: int, present: Present | None) -> set[CardId]:
    """Cards the whenever player taps by hand, or sets a rule to tap, later in the visit it is in now: the babysitter
    waits for the same glance."""
    end = None if present is None else next((b for a, b in present.windows if a <= now <= b), None)
    if present is None or end is None:
        return set()
    return {c for t, c in present.steps if now < t <= end}


def _babysit(s: Save, rules: Rules, glanced: set[CardId], boosts: tuple[str, ...]) -> Save:
    for card in (*(CardId(c) for c in boosts), SMOKE):
        if card not in glanced and tappable(s, rules, card) and blocker(s, rules, card) is None:
            s = _try(s, rules, TapCard(card))
    return s


def _next(s: Save, rules: Rules, babysit: bool, boosts: tuple[str, ...]) -> int | None:
    event = next_event(s, rules)
    times = [event.time] if event is not None else []
    if babysit:
        for card in (*(CardId(c) for c in boosts), SMOKE):
            b = blocker(s, rules, card) if tappable(s, rules, card) else None
            if b is not None and b.ready_at is not None and b.ready_at > s.time:
                times.append(b.ready_at)
    later = [t for t in times if t > s.time]
    return min(later) if later else None


def _note(m: Measured, s: Save, rules: Rules, boosts: tuple[str, ...]) -> None:
    for c in boosts:
        for n in range(1, completions(s, rules, CardId(c)) + 1):
            m.landed.setdefault(f"{c}#{n}", s.time)


def _waste(m: Measured, s: Save, rules: Rules, dt: int) -> None:
    now = running(s, rules)
    for st in s.stores:
        if st.segment.rate == 0 and st.segment.start_value >= store_cap(s, rules, st.store):
            over = floor(exact_net(s, rules, now, st.store))
            if over > 0:
                m.waste[st.store] = m.waste.get(st.store, 0) + over * dt


def compare(w: Measured, b: Measured) -> list[str]:
    """Every way the babysitter ended ahead of (or behind) the whenever player: stores, XP, boost landings, waste."""
    found: list[str] = []
    for a, c in zip(w.save.stores, b.save.stores):
        if a.segment.start_value != c.segment.start_value:
            found.append(f"store {a.store}: whenever {a.segment.start_value / 3_600_000:.2f}, "
                         f"babysitter {c.segment.start_value / 3_600_000:.2f}")
    for a, c in zip(w.save.skills, b.save.skills):
        if a.xp.start_value != c.xp.start_value:
            found.append(f"xp {a.skill}: whenever {a.xp.start_value / 3_600_000:.2f}, "
                         f"babysitter {c.xp.start_value / 3_600_000:.2f}")
    for k in sorted(set(w.landed) | set(b.landed)):
        if w.landed.get(k) != b.landed.get(k):
            found.append(f"{k}: whenever {_h(w.landed.get(k), w.save)}, babysitter {_h(b.landed.get(k), b.save)}")
    for k in sorted(set(w.waste) | set(b.waste)):
        if w.waste.get(k, 0) != b.waste.get(k, 0):
            found.append(f"waste {k}: whenever {w.waste.get(k, 0) / 3_600_000:.2f}, "
                         f"babysitter {b.waste.get(k, 0) / 3_600_000:.2f}")
    return found


def _h(t: int | None, s: Save) -> str:
    return "never" if t is None else f"{t / 3600:.2f}h"
