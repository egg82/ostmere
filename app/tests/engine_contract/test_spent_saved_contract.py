"""SPENT, never stored, and the older invariants it must not disturb (engine DESIGN.txt, "SPENT", invariants 140, 16, 19).
Written blind from that part; MUTANTS_spent.txt names the wrong implementations each test must turn red for."""
import json
from dataclasses import fields
from pathlib import Path

from ashfall_app.engine import (
    CardDef, CardId, FlowKind, RateRef, RunKind, Save, TapCard, advance, decide, decode, encode, explain, value, view,
)
from spent_world import (
    EAT, P, P2, R1, R2, UNITS_PER_BP as U, W, Y, Z, eater, gains, kills, make_run, mixed, plain, pool_for, rate, share_of,
    spent_kind, standard, work_of, world,
)


FIELDS = Path(__file__).resolve().parents[1] / "held/save_fields.json"


@kills(7)
def test_the_save_has_no_field_for_the_yield_and_its_mixes_are_what_the_player_saved():
    """Invariant 140: Save's fields are exactly the held list; after the pool empties the saved mix, the modifiers and the
    pauses hold nothing but what the player and the dry rule wrote (no entry for a gain), and the yield is still read."""
    assert {f.name for f in fields(Save)} == set(json.loads(FIELDS.read_text())["Save"])
    r, s = standard()
    before, after = advance(s, r, 99), advance(s, r, 300)
    assert (after.mixes, after.modifiers, after.orders) == (before.mixes, before.modifiers, before.orders)
    assert [(p.runner, p.store) for p in after.pauses] == [(EAT, P)] and share_of(s, r, R1, 300) == 5000


@kills(7)
def test_a_spent_save_round_trips_and_a_decoded_copy_reads_the_same_yield_later():
    """Invariant 140: decode(encode(s)) == s for a save holding a spent card, and from there stores, views and gains equal
    those of the original at every later t."""
    r, s = standard()
    mid = advance(s, r, 150)
    again = decode(encode(mid, r), r)
    assert again == mid and encode(again, r) == encode(mid, r)
    for t in (150, 151, 400):
        assert view(advance(again, r, t), r) == view(advance(mid, r, t), r), t
        assert [value(again, r, x, t) for x in (P, Y, Z)] == [value(mid, r, x, t) for x in (P, Y, Z)], t
        assert gains(again, r, R1, t) == gains(mid, r, R1, t) == ((EAT, 2500),), t


def test_equal_saves_give_equal_yields_at_every_time():
    """Invariant 140: two saves built apart but equal read the same gains, shares and rates at every t."""
    (r1, s1), (r2, s2) = standard(), standard()
    assert s1 == s2
    for t in (0, 99, 100, 101, 5000):
        assert gains(s1, r1, R1, t) == gains(s2, r2, R1, t) and share_of(s1, r1, R2, t) == share_of(s2, r2, R2, t)
    assert gains(s1, r1, R1, 100) == ((EAT, 2500),)


@kills(23)
def test_invariant_sixteen_dry_never_goes_negative_and_a_spent_card_contributes_nothing():
    """Invariant 16 with a spent card: p is never negative at any time and every line of the spent card explains 0; the
    others' contributions are the effective shares."""
    r, s = standard()
    for t in (0, 50, 99, 100, 101, 1000, 100_000):
        assert value(s, r, P, t) >= 0, t
    for t in (100, 101, 1000):
        for e in (explain(advance(s, r, t), r, RateRef(EAT, FlowKind.COST, P)),
                  explain(advance(s, r, t), r, RateRef(EAT, FlowKind.MAKE, Y)), work_of(s, r, EAT, t)):
            assert (e.run.kind, e.per_hour) == (spent_kind(), 0), t
    assert rate(s, r, Y, 1000) == rate(s, r, P, 1000) == 0 and rate(s, r, Z, 1000) == 5000 * U


@kills(24)
def test_invariant_nineteen_a_hands_tap_yields_the_receivers_and_gives_their_lines_back_at_the_landing():
    """Invariant 19 with a spent card: while the hands tap a 30 s project at 150 every non-paused mix card explains
    YIELDED with per_hour 0 and the share it had (here the effective 5000 and 3000); the spent card stays SPENT; once
    it lands at 180 every line's per_hour is what it was before the tap and the pause is untouched."""
    tap = CardId("tap")
    r = world(eater(), *plain(R1, R2), CardDef(tap, 30))
    s = mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)])
    s = decide(s, r, 150, TapCard(tap))
    for card, store, effective in ((R1, Z, 5000), (R2, W, 3000)):
        e = explain(advance(s, r, 160), r, RateRef(card, FlowKind.MAKE, store))
        assert (e.run.kind, e.per_hour, e.share_bp) == (RunKind.YIELDED, 0, effective), card
    assert make_run(s, r, EAT, 160) == spent_kind() and share_of(s, r, R2, 160) == 3000
    done = advance(s, r, 181)
    assert done.lanes[0].card is None and done.pauses == advance(s, r, 160).pauses
    assert rate(s, r, Z, 181) == 5000 * U
    assert make_run(s, r, R1, 181) == RunKind.FULL


@kills(7)
def test_a_receivers_pause_takes_its_resume_level_from_its_saved_share_not_its_gain():
    """Invariant 140 and QUESTIONS (spent), resume level: R1 costs p2 and receives EAT's share (2500 saved, 5000
    effective from 100). Its pool runs dry at 200, and the Pause it is saved with resumes at one hour of its cost at the
    saved 2500, so no gain is written into the save."""
    r = world(eater(), eater(R1, P2, Z), *plain(R2),
              initial={P: pool_for(4000, 100), P2: pool_for(2500, 100) + pool_for(5000, 100)})
    s = mixed(r, [(EAT, 4000), (R1, 2500), (R2, 1500)])
    assert share_of(s, r, R1, 150) == 5000
    assert [(p.runner, p.store, p.resume_at) for p in advance(s, r, 300).pauses if p.runner == R1] == [
        (R1, P2, pool_for(2500, 3600))]
