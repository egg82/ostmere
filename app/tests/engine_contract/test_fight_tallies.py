"""Invariants 81 (timing does not matter), 84 (tallies) and 86 (no instant), from DESIGN.txt, "FIGHTS", alone."""
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, EventKind, Modifier, ModifierKind, Outcome, Rules, Save, SideStrength, SourceId,
    TapCard, TriggerDef, TriggerId, advance, decode, decide, encode, new_save, next_event, value, view,
)
from contract_gen import few
from fight_world import (
    FOUGHT, HAND, HUNT, LOST, RAID_PER_HOUR, RLOST, STASH, loss_bp, started, world,
)

SPEAR = TriggerDef(TriggerId("spear"), AfterTime(555), Outcome(modifiers=(
    Modifier(SideStrength(HAND), ModifierKind.ADD_BP, 3 * BP, SourceId("spear")),)))
TAPS = (0, 130, 777)                                     # the same decisions at the same times on every path


def play(cuts: list[int], horizon: int, r_p: int = 2) -> Save:
    """The decisions fixed, the reads and the advances sliced at `cuts`: views, next_event, a codec round trip."""
    r = world(r_p, 6, triggers=(SPEAR,))
    s = decide(new_save(r), r, 0, TapCard(HUNT))
    marks = sorted({*cuts, *TAPS, horizon} & set(range(horizon + 1)))
    for at in marks:
        s = advance(s, r, at)
        view(s, r)
        next_event(s, r)
        s = decode(encode(s, r), r)
        if at in TAPS[1:]:
            s = decide(s, r, at, TapCard(HUNT))
    return s


@given(st.lists(st.integers(0, 1500), max_size=6), st.integers(900, 1500), st.integers(0, 5))
@few(20)
def test_any_slicing_with_reads_and_snapshots_reaches_the_same_save(cuts: list[int], horizon: int, p: int):
    """Invariant 81: tallies included (they are stores of the save). The spear lands mid-run on one path's cuts or not."""
    assert play(cuts, horizon, p) == play([], horizon, p)


def test_the_slicing_test_sees_a_fight_it_has_a_tally_that_moved_and_a_spear_that_landed():
    r = world(2, 6, triggers=(SPEAR,))
    s = play([], 1000)
    assert value(s, r, LOST, 1000) > 0 and value(s, r, RLOST, 1000) > 0 and s.fired == (True,)


@given(st.integers(0, 12), st.integers(1, 12), st.integers(1, 30_000))
@few(30)
def test_a_standing_fights_tallies_follow_the_exact_integrals_and_lost_never_passes_fought(p: int, t: int, secs: int):
    """Invariant 84, standing: fought is RAID_PER_HOUR fights an hour (rate units are quantity units per second);
    lost is loss_bp of it. Each is within a whole unit of the exact integral, and lost <= fought."""
    r = world(p, t)
    s = started(r)
    fought, lost = value(s, r, FOUGHT, secs), value(s, r, RLOST, secs)
    exact_fought = RAID_PER_HOUR * secs                       # 1000 rate units a fight an hour, 1 quantity unit a second
    exact_lost = exact_fought * loss_bp(p, t) / BP
    assert 0 <= exact_fought - fought < Q and 0 <= exact_lost - lost < Q
    assert lost <= fought


@given(st.integers(0, 12), st.integers(1, 12), st.integers(1, 5_000))
@few(30)
def test_a_cards_lost_tally_follows_its_work_and_matches_its_completions_at_a_landing(p: int, t: int, secs: int):
    """Invariant 84, card (work_s 100, full share): fought is CardCount. Between landings lost may run ahead of the
    whole completions by the partial one (a rate), never past the work done; at a landing both agree."""
    r = world(p, t)
    s = started(r)
    lost = value(s, r, LOST, secs)
    work_done = secs * Q // 100                               # fights' worth of work, in quantity units
    assert 0 <= work_done * loss_bp(p, t) // BP - lost <= secs and lost <= work_done
    landed = secs // 100 * 100
    exact = (landed // 100) * Q * loss_bp(p, t) / BP
    assert 0 <= exact - value(s, r, LOST, landed) < Q
    assert value(s, r, LOST, landed) <= landed // 100 * Q


def events(rules: Rules, taps: bool) -> list[tuple[int, EventKind, str]]:
    s = new_save(rules)
    s = decide(s, rules, 0, TapCard(HUNT)) if taps else started(rules)
    out: list[tuple[int, EventKind, str]] = []
    while (e := next_event(s, rules)) is not None and e.time <= 2_000 and len(out) < 100:
        out.append((e.time, e.kind, e.subject))
        s = advance(s, rules, e.time)
        if e.kind is EventKind.TAP_DONE:
            s = decide(s, rules, e.time, TapCard(HUNT))
    return out


def test_adding_a_fight_adds_no_event_to_a_tapped_or_a_mixed_run():
    """Invariant 86, with its control: the tap run lands TAP_DONE events and the comparison sees them."""
    for taps in (True, False):
        with_fight = world(3, 5, triggers=(SPEAR,))     # the trigger gives the mixed run an event to compare
        without = replace(with_fight, cards=(replace(with_fight.cards[0], fight=None),),
                          standing=(replace(with_fight.standing[0], fight=None),))
        a, b = events(with_fight, taps), events(without, taps)
        assert a == b
    assert [k for _, k, _ in events(world(3, 5), True)].count(EventKind.TAP_DONE) >= 15
    assert [k for _, k, _ in events(world(3, 5, triggers=(SPEAR,)), False)] == [EventKind.TRIGGER]
    dry = world(3, 5)                                   # control: a fight that drains its store does add events
    dry = replace(dry, stores=tuple(replace(s, initial=10 * Q) if s.id == STASH else s for s in dry.stores))
    assert events(dry, True) != events(replace(dry, cards=(replace(dry.cards[0], fight=None),)), True)
