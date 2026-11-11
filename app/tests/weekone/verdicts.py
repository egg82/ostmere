"""Week one's checks on a played route past B5 (docs/design/days-four-to-seven-plan.md, item 1; combat-plan.md, items 9
and 10): night 7 before the season's turn, what each gathered store loses to its cap away from each chapter's end, the
checks past the sinks over the route's saves, and the 2 AM test across days four to six with the fights running; and
what the readout prints (report.py): each chapter's visit counts (daythree/counters.py) and each calendar day's
arrivals. Ids and numbers only (CLAUDE.md, "Never spoil the owner")."""
from collections import Counter
from functools import cache

from ashfall_app.engine import Save, Verb
from tests.daythree import content as c3
from tests.daythree import counters, plumbing, visits
from tests.daythree.chapter import Later
from tests.daytwo import abs_band
from tests.daytwo.player import QUEUEABLE, DayTwoPlayer, visit_seen
from tests.dayone import capcheck, daily
from tests.dayone.parity import Measured, Present, babysat, replay
from tests.weekone import content as w1
from tests.weekone.routes import week1

CHAPTERS = {"four": w1.day_four(), "five": w1.day_five(), "six": w1.day_six()}
BOOSTS = (*QUEUEABLE, *c3.COMFORTS, w1.WOODSHED, w1.HEARTH_STONES, w1.SPEAR, w1.BEDDING)
"""What the babysitter taps the second it can: day two's queueable steps and the week's staged builds."""
AFTER_END_S = 3600
NIGHT = "N7"
TURN = "B8"


def hour(p: DayTwoPlayer, beat: str) -> float | None:
    at = p.landed_at.get(beat)
    return None if at is None else round((at - p.history[0][0].time) / 3600, 1)


def season_turn_h() -> float:
    """The calendar's turn into the beat B8's day: (target_day - 1) * pace_scale days from the save's start."""
    pace = abs_band.load_pace()
    return (pace.targets[TURN] - 1) * pace.scale * 24


def night_seven(p: DayTwoPlayer) -> list[str]:
    h = hour(p, NIGHT)
    if h is None:
        return [f"{NIGHT} never fell"]
    return [] if h < season_turn_h() else [f"{NIGHT} falls at {h} h, after the season's turn at {season_turn_h():g} h"]


def span(p: DayTwoPlayer, later: Later) -> tuple[int, int]:
    """The visits (1-based, inclusive) a chapter is played in: from the one its first beat is seen in to its last beat's."""
    first, last = visit_seen(p.visits, p.seen_at.get(later.start)), visit_seen(p.visits, p.seen_at.get(later.stop))
    assert first is not None and last is not None, f"{later.start} and {later.stop} were seen"
    return first, last


PARTS = {"four": 9, "five": 16, "six": 9}
"""How many parts a chapter's counting is split into, one per step that changes the mix or queue (the counter's run-ons
cost one to two minutes each; everything else it reads is cheap): each part is its own test's setup, so no test setup
passes the per-test timeout on a slow node. A chapter with more such steps than parts fails `counts_of`."""


_VISITS: dict[int, tuple[DayTwoPlayer, list[counters.Visit]]] = {}
"""A played route's visits (the player is kept so its id stays its own): reading them costs a minute."""


def chapter_visits(p: DayTwoPlayer, chapter: str) -> list[counters.Visit]:
    first, last = span(p, CHAPTERS[chapter])
    if id(p) not in _VISITS:
        _VISITS[id(p)] = (p, visits.visits_of(p))
    return _VISITS[id(p)][1][first - 1:last]


def heavy_steps(p: DayTwoPlayer, chapter: str) -> list[tuple[str, int]]:
    """(visit label, step index) of each step whose reading runs the saves on."""
    return [(v.label, i) for v in chapter_visits(p, chapter) for i, s in enumerate(v.steps) if isinstance(s.verb, counters.MIX_VERBS)]


Decided = dict[tuple[str, int], bool]


@cache
def decided_in(chapter: str, part: int) -> Decided:
    """Whether the part's heavy step decides, kept once read: none (empty) when the chapter has fewer heavy steps than
    `part`."""
    p = week1("typical")
    heavy = heavy_steps(p, chapter)
    assert len(heavy) <= PARTS[chapter], f"{chapter} has {len(heavy)} heavy steps, more than its {PARTS[chapter]} parts"
    if part >= len(heavy):
        return {}
    label, i = heavy[part]
    step = next(v for v in chapter_visits(p, chapter) if v.label == label).steps[i]
    return {(label, i): counters.decides(step, p.rules)}


def typical_decided(chapter: str) -> Decided:
    """The typical route's heavy steps of a chapter, each read by its part."""
    found: Decided = {}
    for part in range(PARTS[chapter]):
        found |= decided_in(chapter, part)
    return found


def counts_of(p: DayTwoPlayer, chapter: str, decided: Decided | None = None) -> list[counters.Counts]:
    """The counters over the visits of one chapter alone, taking the heavy steps' readings from `decided` when given (the
    typical route's, read in `decided_in`'s parts, so a test that follows them pays for the rest only)."""
    found: Decided = {} if decided is None else decided
    return [counters.Counts(v.label, v.gap, len(counters.spendable(v.returned, p.rules)),
                            sum(found[v.label, i] if (v.label, i) in found else counters.decides(s, p.rules)
                                for i, s in enumerate(v.steps))) for v in chapter_visits(p, chapter)]


def spends_of(p: DayTwoPlayer, chapter: str) -> list[int]:
    """The cards on offer at each visit's return that a tap would start at a full store: the counters' spend alone, which
    costs no run-on."""
    return [len(counters.spendable(v.returned, p.rules)) for v in chapter_visits(p, chapter)]


def chapter_counts(p: DayTwoPlayer) -> dict[str, list[counters.Counts]]:
    return {n: counts_of(p, n) for n in CHAPTERS}


def exit_save(p: DayTwoPlayer, later: Later) -> Save:
    """The save at the end of the visit the chapter's last beat is seen in: where its cap-loss check starts."""
    last = span(p, later)[1]
    save = p.visits[last - 1].exit
    assert save is not None
    return save


def cap_loss(p: DayTwoPlayer) -> dict[str, dict[str, tuple[int, ...]]]:
    camp = c3.opening3().camp
    apart = (camp.store,) if camp else ()
    return {n: capcheck.failing(exit_save(p, c), p.rules, apart) for n, c in CHAPTERS.items()}


def plumbed(p: DayTwoPlayer) -> plumbing.Plumbing:
    return plumbing.check(plumbing.sampled(p), p.rules)


def calendar_days(p: DayTwoPlayer) -> list[Counter[str]]:
    """The arrivals by kind of each whole calendar day the route was played through (dayone/daily.py)."""
    return daily.played(p, p.visits[-1].end)


def start(p: DayTwoPlayer) -> int:
    """The exit of the visit before the one B5 is seen in: where the replay starts."""
    first = span(p, CHAPTERS["four"])[0]
    return p.visits[first - 2].end


@cache
def two_am_week(seed: int = 0) -> tuple[Measured, Measured]:
    """The whenever player's decisions from the start of day four replayed as they were and as a babysitter given the same
    reveals, to an hour past G2; the hunt's mix and the standing fights run in both."""
    w = week1("whenever", seed)
    t = start(w)
    i = next(i for i, (s, _) in enumerate(w.history) if s.time >= t)
    s0 = w.history[i][0]
    log: list[tuple[int, Verb]] = [(at, verb) for at, _, verb in w.decisions if at >= s0.time]
    present = Present.of(tuple((v.start, v.end) for v in w.visits), log)
    end = w.landed_at[w.stop_beat()] + AFTER_END_S
    return (replay(w.rules, s0, log, end, False, boosts=BOOSTS),
            replay(w.rules, s0, babysat(log), end, True, present, BOOSTS))
