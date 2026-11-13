"""Week two's checks on a played route through a chapter (docs/design/week-two-plan.md, item 1): what each gathered
store loses to its cap away from the chapter's end, and the 2 AM test from the visit before the chapter's to an hour
past its last beat; and what the readouts print (report.py): the chapter's spine beats beside their target days
(daytwo/abs_band.py), spend and decide on every visit with queuing a stage refused (counters.py), what each absence
between its visits opens, and each calendar day's arrivals; the same for days nine to twelve and for day fifteen,
week three's first, which plays on from day twelve's end. Each takes day eight unless given another chapter. Ids
and numbers only (CLAUDE.md, "Never spoil the owner")."""
import os
from collections import Counter
from functools import cache

from ashfall_app.engine import Save, SetQueue, TapCard, Verb
from tests.daythree import content as c3
from tests.daythree import counters as dc
from tests.daythree import visits
from tests.daythree.chapter import Later
from tests.daytwo import abs_band
from tests.daytwo.checks import returns
from tests.daytwo.player import DayTwoPlayer
from tests.dayone import capcheck, checks, daily
from tests.dayone.parity import Measured, Present, replay_pair
from tests.weekone import verdicts as v1
from tests.weektwo import content as w2
from tests.weektwo import counters, ends
from tests.weektwo.routes import eleven, fifteen, nine, twelve, week2

EIGHT = w2.day_eight("typical")
"""The chapter's span: its start and stop beats are the same on every route."""
NINE = w2.day_nine("typical")
ELEVEN = w2.day_eleven("typical")
TWELVE = w2.day_twelve("typical")
FIFTEEN = w2.day_fifteen("typical")
BEATS = {EIGHT.start: ("B8", "B9"), NINE.start: ("B10",), ELEVEN.start: ("B11",), TWELVE.start: ("B12",),
         FIFTEEN.start: ("B14",)}
"""The spine beats each chapter lands, by the beat it starts at, each held to its band."""
BOOSTS = (*v1.BOOSTS, str(w2.HIDE_FLAPS))
"""What the babysitter taps the second it can: week one's and the chapter's comfort. The build is its order's in both."""
AFTER_END_S = 3600


def days(p: DayTwoPlayer, chapter: Later = EIGHT) -> dict[str, float]:
    """The chapter's spine beats the route reached, in days from the save's start."""
    found = abs_band.reached(p.landed_at, p.history[0][0].time, abs_band.load_pace())
    return {b: d for b, d in found.items() if b in BEATS[chapter.start]}


CHAPTERS = {"eight": EIGHT, "nine": NINE, "eleven": ELEVEN, "twelve": TWELVE, "fifteen": FIFTEEN}
PLAYS = {"eight": week2, "nine": nine, "eleven": eleven, "twelve": twelve, "fifteen": fifteen}
"""Each chapter's typical play is the one its counting reads."""
TRACK_STONES_GAP = ("content gap: stones lose over half their making away from the chapter's end; scavenge fills them "
                    "and field_track, their only sink, is held to the share its roots take allows (about 5400 roots an "
                    "hour at its full share against about 1330 made), where it takes about 110 stones an hour of about "
                    "260 made (open-work.md, item 24)")
TRACK_ROOTS_GAP = ("content gap: roots lose over half their making away from the chapter's end; the lane foragers fill "
                   "them faster than field_track takes them at the share its other inputs allow (open-work.md, item 24)")
STONE_DRY_GAP = ("content gap: dry_wood loses over half its making away from the chapter's end; hand_on_stone fills it, "
                 "and only the fire, the watches and the stews take dry wood (open-work.md, item 24)")
HUNT_PELT_GAP = ("content gap: pelt loses over half its making 24 h away from day twelve's end; hunt_wolf fills it, and "
                 "no pelt sink is in reach (hide_flaps and pelt_bedding are built, hall waits on beams) "
                 "(open-work.md, item 24)")
"""The cap-loss content gaps held as strict xfails, one reason per store over the chapters it fails in; each goes red
once its sink lands."""
PART_STEPS = 1
PARTS = {"eight": 13, "nine": 7, "eleven": 6, "twelve": 11, "fifteen": 14}
"""How many parts a chapter's counting is split into, each the next PART_STEPS heavy steps (counters.heavy) in order, so
each part is its own test's setup and none passes the per-test timeout on a slow node. A chapter with more heavy steps
than its parts hold fails `decided_in`."""
Decided = dict[tuple[str, int], bool]


def chapter_visits(p: DayTwoPlayer, chapter: Later) -> list[dc.Visit]:
    first, last = v1.span(p, chapter)
    return visits.visits_of(p)[first - 1:last]


def heavy_steps(p: DayTwoPlayer, chapter: Later) -> list[tuple[str, int]]:
    """(visit label, step index) of each step whose reading runs the saves on."""
    return [(v.label, i) for v in chapter_visits(p, chapter) for i, s in enumerate(v.steps) if counters.heavy(s, p.rules)]


@cache
def decided_in(chapter: str, part: int) -> Decided:
    """Whether each of the part's heavy steps decides, kept once read: none (empty) when the chapter has fewer heavy
    steps than the part starts at. Read from the saved readings (ends.READINGS) where the saves are present; a step with
    none fails under ends.REQUIRE and is read here otherwise."""
    p, later = PLAYS[chapter]("typical"), CHAPTERS[chapter]
    heavy = heavy_steps(p, later)
    assert len(heavy) <= PARTS[chapter] * PART_STEPS, f"{chapter} has {len(heavy)} heavy steps, more than its parts hold"
    mine = heavy[part * PART_STEPS:(part + 1) * PART_STEPS]
    saved = ends.saved_readings(chapter) if ends.available() else {}
    if os.environ.get(ends.REQUIRE):
        missing = [key for key in mine if key not in saved]
        assert not missing, f"{chapter}'s heavy steps {missing} have no saved reading: {ends.REWRITE}"
    return {key: saved[key] if key in saved else read(p, later, key) for key in mine}


def read(p: DayTwoPlayer, later: Later, key: tuple[str, int]) -> bool:
    """Whether the heavy step at `key` (visit label, step index) of `p`'s chapter `later` decides."""
    label, i = key
    steps = {v.label: v.steps for v in chapter_visits(p, later)}
    return counters.decides(steps[label][i], p.rules)


def typical_decided(chapter: str) -> Decided:
    """The typical route's heavy steps of a chapter, each read by its part."""
    found: Decided = {}
    for part in range(PARTS[chapter]):
        found |= decided_in(chapter, part)
    return found


def counts(p: DayTwoPlayer, chapter: Later = EIGHT, decided: Decided | None = None) -> list[dc.Counts]:
    """The counters over the chapter's visits, taking the heavy steps' readings from `decided` when given (the typical
    route's, read in `decided_in`'s parts, so a test that follows them pays for the rest only)."""
    found: Decided = {} if decided is None else decided
    return [dc.Counts(v.label, v.gap, len(dc.spendable(v.returned, p.rules)),
                      sum(found[v.label, i] if (v.label, i) in found else counters.decides(s, p.rules)
                          for i, s in enumerate(v.steps))) for v in chapter_visits(p, chapter)]


def absences(p: DayTwoPlayer, chapter: Later) -> list[tuple[str, list[str]]]:
    """(label, what opened) for each absence between two of the chapter's visits, counted between the saves the play
    passed through (daytwo/checks.py's reading)."""
    first, last = v1.span(p, chapter)
    vs, back = p.visits[first - 1:last], returns(p)
    return [(f"V{a.index}->V{b.index}", checks.unlocks_between(p.rules, a.exit, back[b.start]))
            for a, b in zip(vs, vs[1:]) if a.exit is not None and b.start in back]


WEEK_ONE_DAYS = 6
"""The whole calendar days week one's plays end inside (they end at about 6.93 days); week one's verdict holds those."""


def calendar_days(p: DayTwoPlayer) -> list[Counter[str]]:
    """The arrivals by kind of each whole calendar day after week one's the route was played through (dayone/daily.py)."""
    return daily.played(p, p.visits[-1].end, c3.opening3())[WEEK_ONE_DAYS:]


def exit_save(p: DayTwoPlayer, chapter: Later = EIGHT) -> Save:
    return v1.exit_save(p, chapter)


def cap_loss(p: DayTwoPlayer, chapter: Later = EIGHT) -> dict[str, tuple[int, ...]]:
    camp = c3.opening3().camp
    return capcheck.failing(exit_save(p, chapter), p.rules, (camp.store,) if camp else ())


@cache
def two_am(seed: int = 0, chapter: str = "eight") -> tuple[Measured, Measured]:
    """The whenever player's decisions from the visit before the chapter's first replayed as they were and as a
    babysitter given the same reveals, to an hour past its last beat; the build's order, the hunt's mix and the
    standing fights run in both. A presence step (Later.queued) the whenever player queued When ready, the babysitter,
    who keeps no queue, taps the second it is ready, as it does the comforts; one the whenever player tapped on its
    return it taps at that tap, as before."""
    play, later = PLAYS[chapter], CHAPTERS[chapter]
    w = play("whenever", seed)
    first = v1.span(w, later)[0]
    t = w.visits[first - 2].end
    i = next(i for i, (s, _) in enumerate(w.history) if s.time >= t)
    s0 = w.history[i][0]
    log: list[tuple[int, Verb]] = [(at, verb) for at, _, verb in w.decisions if at >= s0.time]
    present = Present.of(tuple((v.start, v.end) for v in w.visits), log)
    end = w.landed_at[w.stop_beat()] + AFTER_END_S
    queued = {e.verb.card for _, v in log if isinstance(v, SetQueue) for e in v.entries if isinstance(e.verb, TapCard)}
    boosts = (*BOOSTS, *(str(c) for c in later.queued if c in queued))
    return replay_pair(w.rules, s0, log, end, present, boosts)
