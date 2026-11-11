"""Invariants 158 and 161 (engine DESIGN.txt, "HELD SPEED ...": "Dry pause drops it"): a standing holder paused on a dry
store loses its entries at that instant and every line on its HeldSpeed lanes is rebuilt there; they return at the instant
its Pause resumes; of several holders eating one store that runs short, the dry rule pauses them in reverse rules order and
stops at the first pause that brings the store's net to 0 or above, so the earlier ones keep theirs; and timing does not
matter with a standing holder whose store runs dry and refills.

The store: stew, starting at one item; eat1 and eat2 eat 2 an hour each and mk makes `m` an hour. With m = 3 pausing eat2
alone leaves +1 an hour (net 0 or above), with m = 2 exactly 0, with m = 1 it takes both."""
import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, CardId, FlowKind, Rules, Save, StoreId, TapCard, advance, decide, encode, new_save, value, view,
)
from contract_gen import few
from held_world import first, kills
from heldspeed_world import (
    EAT1, EAT2, GS, HELD, LQ, OUT, OUT2, STEW, WP, WQ, dry_instant, eaters_paused, held_mods, held_of, paused, after, stew_world, hands_mix, plain, rate, resumed, speed_mod, tapped,
)

SHORT = [(3, {EAT2}), (2, {EAT2}), (1, {EAT1, EAT2})]
"""Maker's rate an hour, and who the dry rule pauses at the first dry instant."""


def base_rate(r: Rules, card: CardId, store: StoreId) -> int:
    """The make line's rate with nothing held anywhere: the same rules and taps, a second in."""
    p = plain(r)
    return rate(advance(tapped(p, WP, WQ), p, 1), p, card, FlowKind.MAKE, store).per_hour


def stored(s: Save, r: Rules, store: StoreId, t: int) -> int:
    return value(advance(s, r, t), r, store, t)


@pytest.mark.parametrize(("maker_rate", "who"), SHORT)
@kills(1, 7)
def test_the_dry_rule_pauses_eaters_last_first_and_the_earlier_ones_keep_their_entries(maker_rate: int, who: set[str]):
    """At the dry instant exactly `who` hold a Pause, the paused ones' entries are gone from the stack at that instant
    and the others' stay; just before it, both were held."""
    r, s = stew_world(maker_rate)
    d = dry_instant(r, s)
    assert [m.source for m in held_mods(advance(s, r, d.time - 1), r)] == [HELD + EAT1, HELD + EAT2]
    assert eaters_paused(d) == who
    assert [m.source for m in held_mods(d, r)] == [HELD + a for a in (EAT1, EAT2) if a not in who]


@kills(1, 7)
def test_the_lines_of_a_paused_eaters_lane_are_rebuilt_at_the_dry_instant_and_the_fed_lane_keeps_its_speed():
    """m = 3: at the instant eat2 pauses, wq's make rate is its base while wp's stays at 15000 / BP of its base, read at
    that very instant."""
    r, s = stew_world(3)
    d = dry_instant(r, s)
    base_wq = base_rate(r, WQ, OUT2)
    base_wp = base_rate(r, WP, OUT)
    assert rate(d, r, WQ, FlowKind.MAKE, OUT2).per_hour == base_wq
    assert rate(d, r, WP, FlowKind.MAKE, OUT).per_hour == base_wp * (BP + 5000) // BP


@kills(1)
def test_the_paused_lane_works_at_its_base_speed_for_as_long_as_the_eater_is_paused():
    """m = 3 (eat2 paused from 3600 to 10800): wq's store gained at 13000 / BP of a second's work before the pause and at
    exactly one a second inside it, while wp, fed throughout, keeps 15000 / BP."""
    r, s = stew_world(3)
    d = dry_instant(r, s)
    assert paused(d, EAT2) and d.time == 3600
    assert abs(stored(d, r, OUT2, d.time + 1000) - stored(d, r, OUT2, d.time) - 1000 * Q) <= 1000
    assert abs(stored(d, r, OUT2, d.time) - d.time * Q * (BP + 3000) // BP) <= d.time
    assert abs(stored(d, r, OUT, d.time + 1000) - stored(d, r, OUT, d.time) - 1000 * Q * (BP + 5000) // BP) <= 1000


@kills(8)
def test_a_resumed_eater_gets_its_entry_back_at_its_resume_instant_and_not_a_moment_before():
    r, s = stew_world(3)
    d = dry_instant(r, s)
    n = resumed(r, d, EAT2)
    assert n.time > d.time
    assert held_of(advance(d, r, n.time - 1), r, EAT2) == []
    assert held_of(n, r, EAT2) == [speed_mod(EAT2, LQ, 3000)]
    assert [h.card for h in view(n, r).held] == [EAT1, EAT2]
    assert rate(n, r, WQ, FlowKind.MAKE, OUT2).per_hour == base_rate(r, WQ, OUT2) * (BP + 3000) // BP


@kills(1, 8)
def test_the_entry_comes_and_goes_with_each_pause_of_a_store_that_dries_again_and_refills():
    """m = 3: eat2 pauses at 3600, resumes at 10800, and pauses again once the refilled store runs out: each pause drops
    its entry at its own instant and each resume returns it at its own."""
    r, s = stew_world(3)
    d1 = dry_instant(r, s)
    n1 = resumed(r, d1, EAT2)
    d2 = _next_pause(r, n1)
    assert d1.time < n1.time < d2.time
    for save, held in ((d1, False), (n1, True), (d2, False)):
        assert bool(held_of(save, r, EAT2)) is held, save.time
        assert bool(held_of(save, r, EAT1)), save.time


def _next_pause(r: Rules, s: Save) -> Save:
    return first(s, r, lambda x: paused(x, EAT2))


@few(10)
@given(wq_at=st.integers(1, 5000), gs_at=st.integers(1, 9000), cuts=st.lists(st.integers(1, 3000), min_size=1, max_size=5),
       end=st.integers(30_000, 60_000), gs_share=st.integers(1, BP))
@kills(1, 8)
def test_timing_does_not_matter_with_a_standing_holder_whose_store_runs_dry_and_refills(
        wq_at: int, gs_at: int, cuts: list[int], end: int, gs_share: int):
    """Invariant 161: the same decisions at the same times, reached by one advance or by slices with views and snapshots
    between, give equal saves at `end`, the stores included, across several dry and refill cycles."""
    r = stew_world(3)[0]

    def play(step: str) -> Save:
        def go(x: Save, t: int) -> Save:
            if step == "direct":
                return advance(x, r, t)
            for c in sorted({min(x.time + c, t) for c in cuts}):
                x = advance(x, r, c)
                view(x, r)
                encode(x, r)
            return advance(x, r, t)

        x = decide(new_save(r), r, 0, TapCard(WP))
        x = decide(go(x, wq_at), r, wq_at, TapCard(WQ))
        return go(after(go(x, wq_at + gs_at), r, *hands_mix((GS, gs_share))), end)

    a, b = play("direct"), play("sliced")
    assert a == b
    assert [value(a, r, st_, end) for st_ in (OUT, OUT2, STEW)] == [value(b, r, st_, end) for st_ in (OUT, OUT2, STEW)]
