"""Day eight's decide counter proven able to fail (docs/design/week-two-plan.md, item 1): a step whose only change is a
queued stage of a staged build, one day three's counter counts as a decision (it moves which goal lands first), is
refused by week two's; the counter still counts the chapter's real decisions; and it counts a change that moves a
fight's odds or a goal's landing (the watch shifts below trade a build against the pack) and not one that moves nothing.
The queued stages are week one's own (day six's bedding, queued a stage a visit), since day eight queues none."""
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from ashfall_app.engine import CardId, CardShare, Mix, Rules, Save, SaveMix, SetQueue, TapCard, decide, rebase, view
from ashfall_app.engine.codec import canonical
from ashfall_app.opening.renames import engine_renames, load_renames
from tests.daythree import counters as c3
from tests.daythree import shifts, visits
from tests.daythree.content import rules3
from tests.daythree.counters import Step
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone import absence, daily, sinks
from tests.weekone import verdicts as v1
from tests.weektwo import counters
from tests.weektwo import verdicts as v2
from tests.weektwo.routes import week_one

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def queued_stages() -> tuple[DayTwoPlayer, list[Step]]:
    """Week one's typical steps in day six that queue a staged build's stage and that day three's counter counts."""
    p = week_one("typical")
    first, last = v1.span(p, v1.CHAPTERS["six"])
    steps = [s for v in visits.visits_of(p)[first - 1:last] for s in v.steps if isinstance(s.verb, SetQueue)]
    return p, [s for s in steps if counters.queues_a_stage(s, p.rules) and c3.decides(s, p.rules)]


@pytest.fixture(scope="module")
def refused(queued_stages: tuple[DayTwoPlayer, list[Step]]) -> list[bool]:
    p, steps = queued_stages
    return [counters.decides(s, p.rules) for s in steps]


def test_a_step_whose_only_change_is_a_queued_stage_is_refused(refused: list[bool]):
    assert refused, "day six has a queued stage day three's counter counts"
    assert not any(refused)


def test_the_counter_still_counts_a_real_decision(eight_counts: tuple[DayTwoPlayer, list[c3.Counts]]):
    _, found = eight_counts
    assert any(c.decide > 0 for c in found)


WATCH, STAKES, FORAGE = CardId("n2_watch"), CardId("n2_stakes"), CardId("n2_forage")
KEEP, MEND = CardId("n4_watch"), CardId("n4_mend")
N2, N4 = (WATCH, STAKES, FORAGE), (KEEP, MEND)
"""Two people's lanes: the first's watch, stakes (the palisade's input) and forage; the second's watch and mending. One
person's shares sum to at most 100%."""


@dataclass(frozen=True)
class Read:
    """What the counters make of one step: the shifts, the old reading (which of two goals lands first), the verdict."""

    shift: shifts.Shift
    orders: bool
    decides: bool


def read(rules: Rules, step: Step) -> Read:
    assert step.return_at is not None
    return Read(shifts.shift(step.before, step.after, rules, step.return_at), c3.moves_the_order(step, rules),
                counters.decides(step, rules))


PACK_SAVE = Path(__file__).resolve().parent / "captured" / "eight-typical-pack.json"
"""A real save the reads start from, so day eight's pacing does not move them: {commit, route, visit, next_return,
save}, `save` being encode()'s envelope as JSON (canonical() gives back its text)."""


def pack_save(rules: Rules) -> tuple[Save, int]:
    """The captured save rebased onto `rules`, each trip set once to the share the player's own tuning reads off the
    page's preview (sinks.tuned_share): the capture was written with holds, whose shares run a trip dry and back every
    minute without them. The town's split, which the examples below are written for, is the capture's. And when its
    next visit starts."""
    raw = json.loads(PACK_SAVE.read_text())
    at = rebase(canonical(raw["save"]), rules, engine_renames(load_renames()))
    mix = next(m for m in at.mixes if m.id == at.active)
    for trip, share in [(t, sinks.tuned_share(rules, at, t)) for t in v2.EIGHT.sinks.trips]:
        mix = sinks.with_share(mix, trip.card, share)
    return decide(at, rules, at.time, SaveMix(mix)), raw["next_return"]


def reshared(rules: Rules, at: Save, nxt: int, lane: tuple[CardId, ...], shares: dict[CardId, int]) -> Step:
    """Saving the town mix with one person's `lane` set to `shares` (a card of the lane not named is dropped)."""
    mix = next(m for m in at.mixes if str(m.id) == "town:camp")
    kept = tuple(c for c in mix.components if not (isinstance(c, CardShare) and c.card in lane))
    verb = SaveMix(Mix(mix.id, (*kept, *(CardShare(c, bp) for c, bp in shares.items() if bp))))
    return Step(at.time, verb, at, decide(at, rules, at.time, verb), nxt)


@pytest.fixture(scope="module")
def reads() -> dict[str, Read]:
    """Steps on main's eight-typical save at the pack's first visit (V37, captured from 86eb6f8b), read once in setup."""
    rules = rules3()
    at, nxt = pack_save(rules)
    blocked = next(c.card for c in view(at, rules).cards if c.cap is not None and c.blocker is not None)
    steps = {"trade": reshared(rules, at, nxt, N2, {WATCH: 10_000}),
             "odds": reshared(rules, at, nxt, N4, {MEND: 7_500, KEEP: 2_500}),
             "finish": reshared(rules, at, nxt, N2, {STAKES: 2_500, WATCH: 2_500, FORAGE: 5_000}),
             "nudge": reshared(rules, at, nxt, N2, {STAKES: 5_100, FORAGE: 4_900}),
             "same": reshared(rules, at, nxt, N2, {STAKES: 5_000, FORAGE: 5_000}),
             "refused": Step(at.time, TapCard(blocked), at, at, nxt)}
    return {k: read(rules, s) for k, s in steps.items()}


def test_a_watch_shift_trading_the_palisades_landing_for_the_packs_odds_is_a_decision(reads: dict[str, Read]):
    """One person from the stakes to the watch: the pack is likelier to be held, the palisade lands hours later. The
    old reading (which of two goals lands first) sees one goal and counts nothing."""
    r = reads["trade"]
    assert r.shift.odds_bp >= c3.ODDS_MIN_BP and r.shift.finish_s >= c3.FINISH_MIN_S
    assert not r.orders and r.decides


def test_each_kind_of_shift_is_a_decision_alone(reads: dict[str, Read]):
    """Three quarters of the second person's time from the watch to mending moves the pack's odds only (all of it also
    moves the watch's store past the level reading, now a fed person's watch runs faster); the first's stakes to the
    watch moves the palisade's landing only. Each counts, and each fails the other two readings. A level-only move has no example on
    this save: roots and stones are full and every move that changes another store's level moves a landing, so the
    level-only rule is held by test_a_level_only_shift_is_a_decision, and the engine's level reading by the nudge."""
    odds, finish = (reads[k].shift for k in ("odds", "finish"))
    assert odds.odds_bp >= c3.ODDS_MIN_BP and odds.finish_s < c3.FINISH_MIN_S and odds.level_bp < c3.LEVEL_MIN_BP
    assert finish.finish_s >= c3.FINISH_MIN_S and finish.odds_bp < c3.ODDS_MIN_BP and finish.level_bp < c3.LEVEL_MIN_BP
    assert all(reads[k].decides and not reads[k].orders for k in ("odds", "finish"))


def test_a_level_only_shift_is_a_decision():
    """The counter's rule (counters.meaningful, which moves_the_return and so decides apply): a shift whose only
    reading at its threshold is a store's level counts; one a basis point under does not."""
    assert c3.meaningful(shifts.Shift(0, 0, c3.LEVEL_MIN_BP))
    assert not c3.meaningful(shifts.Shift(0, 0, c3.LEVEL_MIN_BP - 1))


def test_a_share_change_that_moves_no_odds_and_no_landing_is_no_decision(reads: dict[str, Read]):
    """A fiftieth of one person's time from forage to stakes: it moves a store a hair and nothing the player sees."""
    r = reads["nudge"]
    assert (r.shift.odds_bp, r.shift.finish_s) == (0, 0) and 0 < r.shift.level_bp < c3.LEVEL_MIN_BP
    assert not r.decides


def test_saving_the_same_mix_or_tapping_a_card_that_does_not_start_is_no_decision(reads: dict[str, Read]):
    for name in ("same", "refused"):
        assert reads[name].shift == shifts.Shift(0, 0, 0)
        assert not reads[name].decides


@pytest.fixture(scope="module")
def stage_landings(queued_stages: tuple[DayTwoPlayer, list[Step]]) -> list[tuple[int, bool]]:
    """Each queued stage's own landing shift, and whether the return reading would count it."""
    p, steps = queued_stages
    return [(shifts.shift(s.before, s.after, p.rules, s.return_at or s.at + c3.FALLBACK_S).finish_s,
             c3.moves_the_return(s, p.rules)) for s in steps]


def test_a_queued_stage_moves_its_own_landing_and_is_still_refused(stage_landings: list[tuple[int, bool]]):
    """The stage's landing moves by hours (so the landing reading would count it); the refusal is what stops it."""
    assert stage_landings, "day six has a queued stage"
    assert all(finish >= c3.FINISH_MIN_S for finish, _ in stage_landings)
    assert not any(counted for _, counted in stage_landings)


@pytest.mark.parametrize("week_days", [("nine", "typical")], indirect=True)
def test_a_dead_day_is_found_among_the_second_weeks_real_ones(week_days: tuple[DayTwoPlayer, list[Counter[str]]]):
    """As week one's control: a window whose two ends are one state counts nothing, one with only lines counts as dead
    too, and swapped into the real days each is the one found."""
    p, days = week_days
    assert len(days) >= 2 and daily.empty_days(days) == []
    v = view(p.history[-1][0], p.rules)
    dead, _ = absence.counts(p.rules, v, v, ())
    assert sum(dead.values()) == 0
    lines_only = Counter(line=days[0]["line"])
    assert lines_only["line"] > 0
    assert daily.empty_days([dead, *days[1:]]) == [1]
    assert daily.empty_days([*days[:1], lines_only, *days[2:]]) == [2]
