"""The human-paced player model (human.py, human_flags.py): it plays day one, its data file parses and every threshold
names a source or is a design choice, and its flaggers fire on planted input. What it finds is a report
(python -m tests.dayone.report --human), never a failure."""
from pathlib import Path

import pytest

from ashfall_app.engine import Unlock
from tests.dayone import human_flags as hf
from tests.dayone.beats import questions_open
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.human import THRESHOLDS, HumanPlayer, human_schedule, thresholds
from tests.dayone.player import DayOnePlayer

Run = tuple[HumanPlayer, list[hf.Session]]
Unlocks = tuple[dict[Unlock, str], dict[Unlock, str]]


def test_the_data_file_parses_and_every_threshold_has_a_source():
    th = thresholds()
    assert th.unsourced() == []
    assert th.dead_gap in th.entries and "dead_gap_research_s" in th.entries
    assert th.dead_gap_s() == 180


def test_a_threshold_with_no_source_is_found(tmp_path: Path):
    bad = tmp_path / "t.toml"
    bad.write_text(THRESHOLDS.read_text() + '\n[threshold.invented]\nvalue = 1\nunit = "s"\nsource = "somebody said"\n')
    assert thresholds(bad).unsourced() == ["invented"]


def test_the_visits_are_a_seeded_spread_over_waking_days():
    th = thresholds()
    a, b = human_schedule(0, th), human_schedule(0, th)
    assert a == b and a != human_schedule(1, th)
    gaps = [v.start - (u.start + u.length) for u, v in zip(a.visits, a.visits[1:])]
    nights = [g for g in gaps if g >= th.v("night_h") * 3600]
    assert 0 < len(nights) < len(gaps) and len(nights) == len(gaps) // round(th.v("visits_per_day"))


def test_a_planted_leave_naming_nothing_is_a_bored_leave():
    def s(leave: hf.Leave | None) -> hf.Session:
        return hf.Session("V9", 0, 60, ((0, "level"),), (), leave)
    assert hf.bored(s(hf.Leave((), frozenset())))
    assert not hf.bored(s(hf.Leave((("level", "foraging", 600),), frozenset())))
    assert not hf.bored(s(None))


def test_a_planted_dead_stretch_is_flagged():
    assert hf.dead_stretches(0, 700, [0, 60, 600, 650], 180) == [(60, 600)]
    assert hf.dead_stretches(0, 700, [0, 100, 250, 400, 550, 700], 180) == []
    assert hf.dead_stretches(0, 700, [0, 60], 180) == [(60, 700)]


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_the_model_plays_day_one_and_records_each_session(human_run: Run):
    p, found = human_run
    assert "B3" in p.seen_at and 0 < p.read_lines <= len(p.lines)
    assert [s.label for s in found] == ["opening", *(f"V{v.index}" for v in p.visits)]
    assert all(s.notables for s in found) and found[0].leave is None
    assert all(s.leave is not None for s in found[1:])
    cap = thresholds().v("session_s")
    assert any(v.end - v.start < cap for v in p.visits), "no visit ended before session_s: the player never left"


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_the_real_session_flagger_fires_and_stays_quiet(human_run: Run):
    _, found = human_run
    s = found[2]
    times = [t for t, _ in s.notables]
    assert hf.dead_stretches(s.start, s.end, times, 1)
    assert hf.dead_stretches(s.start, s.end, times, 10**9) == []


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_a_leave_names_its_payoffs_and_open_questions(human_run: Run):
    p, found = human_run
    leaves = [s.leave for s in found if s.leave is not None]
    assert all(kind in hf.PAYOFFS and secs > 0 for lv in leaves for kind, _, secs in lv.payoffs)
    h1 = p.seen_at["H1"]
    assert questions_open(["H1"]) and not questions_open([])
    assert all(lv.questions for s in found if (lv := s.leave) and s.end >= h1)


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_earned_and_fixed_time_unlocks_are_told_apart(unlock_runs: Unlocks):
    same_visits, _ = unlock_runs
    assert set(same_visits.values()) <= {hf.EARNED, hf.FIXED} and hf.FIXED in same_visits.values()


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_the_players_who_skip_the_tools_land_behind_the_typical_route(unlock_runs: Unlocks):
    """by_hand (no rules, no queue, the same visits) and lazy (once a day) each land some unlock later than typical by
    more than unlock_margin_s, or never. They are reported, never held to a floor; this gap is the one check on them."""
    no_tools, less_present = unlock_runs
    assert hf.lands_behind(no_tools), "by_hand lands every unlock with typical"
    assert hf.lands_behind(less_present), "lazy lands every unlock with typical"


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
@pytest.mark.parametrize("day_route", [("typical", 0)], indirect=True)
def test_an_equal_landing_is_not_behind(day_route: DayOnePlayer):
    """The planted control: a route against itself lands every unlock at the same time, so it is not behind."""
    kinds = hf.classify(day_route, day_route, thresholds().v("unlock_margin_s"))
    assert kinds and not hf.lands_behind(kinds)


def test_a_run_of_only_fixed_time_moments_is_flagged():
    def m(at: int, label: str) -> hf.Moment:
        return hf.Moment(at, (), label)
    mixed = [m(0, hf.FIXED), m(1, hf.EARNED), m(2, hf.FIXED), m(3, hf.UNKNOWN), m(4, hf.FIXED)]
    assert hf.fixed_runs(mixed, 2) == []
    planted = [m(0, hf.FIXED), m(1, hf.EARNED), m(2, hf.FIXED), m(3, hf.FIXED), m(4, hf.FIXED)]
    assert [[x.at for x in r] for r in hf.fixed_runs(planted, 2)] == [[2, 3, 4]]
    assert {d: dict(c) for d, c in hf.per_day(planted).items()} == {1: {hf.FIXED: 4, hf.EARNED: 1}}


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
@pytest.mark.parametrize("day_route", [("typical", 0)], indirect=True)
def test_a_stage_the_poorer_route_reaches_late_or_never_is_earned(day_route: DayOnePlayer):
    """The planted controls: the poorer route is the good one with one stage moved much later, one dropped, one nudged
    within the margin; the rest are the same time."""
    assert day_route.end_at is not None
    margin = thresholds().v("unlock_margin_s")
    first = sorted((t, s) for s, t in day_route.stage_at.items() if t > day_route.end_at)
    late, never, near = (s for _, s in first[:3])
    poor = dict(day_route.stage_at)
    poor[late] += int(margin) + 1
    del poor[never]
    poor[near] += int(margin)
    worse = day_route.fork()
    worse.stage_at = poor
    kinds = hf.classify_stages(day_route, worse, margin)
    assert (kinds[late], kinds[never], kinds[near]) == (hf.EARNED, hf.EARNED, hf.FIXED)
    assert {k for s, k in kinds.items() if s not in (late, never)} == {hf.FIXED}
    assert set(hf.classify_stages(day_route, day_route, margin).values()) == {hf.FIXED}


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
@pytest.mark.parametrize("day_route", [("typical", 0)], indirect=True)
def test_a_moment_of_only_stages_takes_the_stages_verdict(day_route: DayOnePlayer):
    assert day_route.end_at is not None
    stage = min((t, s) for s, t in day_route.stage_at.items() if t > day_route.end_at)[1]
    for verdict in (hf.EARNED, hf.FIXED):
        kinds: dict[hf.Landing, str] = {**dict.fromkeys(day_route.unlocked_at, hf.FIXED), **dict.fromkeys(day_route.stage_at, hf.FIXED)}
        found = hf.moments(day_route, {**kinds, stage: verdict}, 60)
        assert [m.label for m in found if stage in m.stages] == [verdict]
